import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import ElConfigProvider from 'element-plus/es/components/config-provider/index'
import ElInput from 'element-plus/es/components/input/index'
import ElSelect, { ElOption } from 'element-plus/es/components/select/index'
import ElTable, { ElTableColumn } from 'element-plus/es/components/table/index'
import 'element-plus/theme-chalk/base.css'
import 'element-plus/theme-chalk/el-config-provider.css'
import 'element-plus/theme-chalk/el-icon.css'
import 'element-plus/theme-chalk/el-input.css'
import 'element-plus/theme-chalk/el-message.css'
import 'element-plus/theme-chalk/el-notification.css'
import 'element-plus/theme-chalk/el-option.css'
import 'element-plus/theme-chalk/el-overlay.css'
import 'element-plus/theme-chalk/el-popper.css'
import 'element-plus/theme-chalk/el-scrollbar.css'
import 'element-plus/theme-chalk/el-select.css'
import 'element-plus/theme-chalk/el-table-column.css'
import 'element-plus/theme-chalk/el-table.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElConfigProvider)
app.use(ElInput)
app.use(ElOption)
app.use(ElSelect)
app.use(ElTable)
app.use(ElTableColumn)

app.mount('#app')
