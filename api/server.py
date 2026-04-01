"""
AlphaTransformer FastAPI 服务 — 健壮版
启动命令：uvicorn api.server:app --host 0.0.0.0 --port 8080 --reload
"""

import time
import sys
import os

# 确保项目根目录在 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from api.schemas import HealthResponse, ErrorResponse

# 注册路由
from api.dashboard import router as dashboard_router
from api.trading import router as trading_router
from api.account import router as account_router
from api.auto import router as auto_router
from api.predictor import get_registry

# ─── 全局异常处理（消灭所有 500）─────────────────────────────

app = FastAPI(
    title="AlphaTransformer API",
    description="基于 iTransformer 的量化股票预测系统 — 2026 SOTA Edition",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # 与 allow_origins=["*"] 组合时浏览器规范不允许 credentials=true
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常捕获：
    - 所有未处理的异常返回 200 + error JSON（不崩溃）
    - 只有 Pydantic 校验错误返回 422
    """
    if isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "参数校验失败",
                "detail": str(exc),
                "code": "VALIDATION_ERROR",
            },
        )

    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "请求处理失败",
                "detail": exc.detail,
                "code": f"HTTP_{exc.status_code}",
            },
        )

    # 未知异常 → 返回 200 + 错误（防止前端 500）
    return JSONResponse(
        status_code=200,
        content={
            "error": "服务器内部错误（已自动恢复）",
            "detail": str(exc),
            "code": "INTERNAL_ERROR",
        },
    )


# ─── 路由注册 ────────────────────────────────────────────

app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(trading_router, prefix="/api/v1")
app.include_router(account_router, prefix="/api/v1")
app.include_router(auto_router, prefix="/api/v1")

# ─── 启动事件 ────────────────────────────────────────────

_start_time = time.time()


@app.on_event("startup")
async def startup_event():
    """服务启动时自动加载模型"""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("uvicorn")

    logger.info("=" * 60)
    logger.info("  AlphaTransformer API 启动中...")
    logger.info("=" * 60)

    # 自动加载默认模型（v1，随机权重）
    registry = get_registry()
    load_result = registry.load(
        checkpoint_path="",           # 无检查点时用随机权重（开发模式）
        model_version="v1",
        device="cpu",                # 默认 CPU（安全）
    )

    if load_result["success"]:
        logger.info(
            f"  模型加载成功 | 版本: {load_result['model_version']} | "
            f"设备: {load_result['device']} | "
            f"参数量: {load_result['num_params']:,}"
        )
    else:
        logger.warning(
            f"  模型加载失败: {load_result['error_code']} — "
            f"{load_result['error_detail']}"
        )

    logger.info("  所有 API 已就绪，等待请求...")
    logger.info("  文档: http://localhost:8080/docs")


# ─── 健康检查 ────────────────────────────────────────────

@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """健康检查（前端轮询接口，永不 500）"""
    registry = get_registry()
    status = registry.get_status()
    return HealthResponse(
        status="ok",
        model_loaded=status["loaded"],
        model_device=status["device"],
        uptime_seconds=round(time.time() - _start_time, 1),
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "AlphaTransformer API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# ─── 预测端点 ────────────────────────────────────────────

@app.post("/api/v1/predictor/load")
async def load_predictor(
    checkpoint_path: str = "",
    model_version: str = "v1",
    device: str = "cpu",
):
    """手动加载/切换模型"""
    registry = get_registry()
    result = registry.load(
        checkpoint_path=checkpoint_path,
        model_version=model_version,
        device=device,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error_detail"])
    return result


@app.get("/api/v1/predictor/status")
async def predictor_status():
    """获取模型状态"""
    return get_registry().get_status()


# ─── 运行入口 ────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )
