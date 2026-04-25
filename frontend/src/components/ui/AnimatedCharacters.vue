<template>
  <div ref="wrapperRef" class="characters-container">
    <svg 
      class="characters-svg"
      viewBox="0 0 500 400"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      <!-- Background elements -->
      <circle cx="420" cy="60" r="25" fill="#FFD93D" opacity="0.6"/>
      <circle cx="80" cy="80" r="15" fill="#6BCB77" opacity="0.5"/>
      <circle cx="450" cy="350" r="20" fill="#4D96FF" opacity="0.5"/>
      
      <!-- Grid lines for decoration -->
      <line x1="0" y1="380" x2="500" y2="380" stroke="#e0e0e0" stroke-width="1"/>
      <line x1="0" y1="360" x2="500" y2="360" stroke="#f0f0f0" stroke-width="0.5"/>

      <!-- Orange Circle Character (left) -->
      <g ref="orangeRef" :style="{ transform: `translateY(${orangeY}px)`, transition: 'transform 0.4s ease' }">
        <circle 
          cx="100" 
          cy="280" 
          r="50" 
          :fill="isHidingPassword ? '#FFD93D' : '#FF6B6B'"
          class="character-body"
        />
        <!-- Eyes -->
        <circle cx="82" cy="270" r="8" fill="white"/>
        <circle :cx="82 + orangePupil.x" :cy="270 + orangePupil.y" r="4" fill="#333"/>
        <circle cx="118" cy="270" r="8" fill="white"/>
        <circle :cx="118 + orangePupil.x" :cy="270 + orangePupil.y" r="4" fill="#333"/>
        <!-- Mouth -->
        <path 
          v-if="!isHidingPassword" 
          :d="isTyping ? 'M85 295 Q100 305 115 295' : 'M88 295 L112 295'" 
          stroke="white" 
          stroke-width="2" 
          fill="none"
          stroke-linecap="round"
        />
        <path 
          v-else 
          d="M85 298 Q100 288 115 298" 
          stroke="white" 
          stroke-width="2" 
          fill="none"
          stroke-linecap="round"
        />
      </g>

      <!-- Purple Tall Rectangle (back center) -->
      <g ref="purpleRef" :style="{ transform: `translateY(${purpleY}px)`, transition: 'transform 0.4s ease' }">
        <rect 
          x="160" 
          y="130" 
          width="70" 
          height="160" 
          rx="12" 
          fill="#9775FA"
          class="character-body"
        />
        <!-- Eyes -->
        <ellipse cx="180" cy="200" rx="10" ry="12" fill="white"/>
        <circle :cx="180 + purplePupil.x" :cy="200 + purplePupil.y" r="5" fill="#333"/>
        <ellipse cx="210" cy="200" rx="10" ry="12" fill="white"/>
        <circle :cx="210 + purplePupil.x" :cy="200 + purplePupil.y" r="5" fill="#333"/>
        <!-- Mouth -->
        <path 
          v-if="!isHidingPassword && !isTyping" 
          d="M175 235 L205 235" 
          stroke="white" 
          stroke-width="2" 
          stroke-linecap="round"
        />
        <path 
          v-else-if="isTyping" 
          d="M170 235 Q190 250 210 235" 
          stroke="white" 
          stroke-width="2" 
          fill="none"
          stroke-linecap="round"
        />
        <path 
          v-else 
          d="M175 240 Q190 230 205 240" 
          stroke="white" 
          stroke-width="2" 
          fill="none"
          stroke-linecap="round"
        />
        <!-- Blush when password hidden -->
        <circle v-if="isHidingPassword" cx="170" cy="225" r="8" fill="#FF8E8E" opacity="0.6"/>
        <circle v-if="isHidingPassword" cx="215" cy="225" r="8" fill="#FF8E8E" opacity="0.6"/>
      </g>

      <!-- Black Main Square Character (center) -->
      <g ref="blackRef" :style="{ transform: `translateY(${blackY}px)`, transition: 'transform 0.4s ease' }">
        <rect 
          x="250" 
          y="100" 
          width="100" 
          height="180" 
          rx="16" 
          :fill="isHidingPassword ? '#333' : '#1a1a1a'"
          class="character-body main-character"
        />
        <!-- White inner border -->
        <rect 
          x="258" 
          y="108" 
          width="84" 
          height="164" 
          rx="12" 
          fill="none" 
          stroke="white" 
          stroke-width="1"
          opacity="0.3"
        />
        <!-- Eyes -->
        <ellipse cx="280" cy="170" rx="14" ry="16" fill="white"/>
        <circle :cx="280 + blackPupil.x" :cy="170 + blackPupil.y" r="7" fill="#00D9FF"/>
        <circle :cx="280 + blackPupil.x - 2" :cy="170 + blackPupil.y - 2" r="2" fill="white" opacity="0.8"/>
        <ellipse cx="320" cy="170" rx="14" ry="16" fill="white"/>
        <circle :cx="320 + blackPupil.x" :cy="170 + blackPupil.y" r="7" fill="#00D9FF"/>
        <circle :cx="320 + blackPupil.x - 2" :cy="170 + blackPupil.y - 2" r="2" fill="white" opacity="0.8"/>
        
        <!-- Eye shine when looking -->
        <template v-if="isLookingAtEachOther">
          <circle cx="278" cy="165" r="3" fill="white" opacity="0.5"/>
          <circle cx="318" cy="165" r="3" fill="white" opacity="0.5"/>
        </template>
        
        <!-- Mouth -->
        <path 
          v-if="!isHidingPassword && !isTyping" 
          d="M275 215 L325 215" 
          stroke="white" 
          stroke-width="3" 
          stroke-linecap="round"
        />
        <path 
          v-else-if="isTyping" 
          d="M270 215 Q300 235 330 215" 
          stroke="white" 
          stroke-width="3" 
          fill="none"
          stroke-linecap="round"
        />
        <path 
          v-else 
          d="M275 220 Q300 205 325 220" 
          stroke="white" 
          stroke-width="3" 
          fill="none"
          stroke-linecap="round"
        />
        
        <!-- Blush marks -->
        <circle v-if="isHidingPassword" cx="265" cy="200" r="10" fill="#FF6B6B" opacity="0.5"/>
        <circle v-if="isHidingPassword" cx="335" cy="200" r="10" fill="#FF6B6B" opacity="0.5"/>
        
        <!-- Sweat drop when peeking password -->
        <path 
          v-if="isPurplePeeking && props.passwordLength > 0" 
          d="M350 130 Q355 145 350 150 Q345 145 350 130" 
          fill="#4D96FF"
          opacity="0.8"
        />
      </g>

      <!-- Yellow Irregular Character (right) -->
      <g ref="yellowRef" :style="{ transform: `translateY(${yellowY}px)`, transition: 'transform 0.4s ease' }">
        <path 
          d="M380 200 L420 200 L430 280 L370 280 Z" 
          fill="#FFD93D"
          class="character-body"
        />
        <!-- Eyes -->
        <circle cx="392" cy="230" r="7" fill="white"/>
        <circle :cx="392 + yellowPupil.x" :cy="230 + yellowPupil.y" r="3.5" fill="#333"/>
        <circle cx="408" cy="230" r="7" fill="white"/>
        <circle :cx="408 + yellowPupil.x" :cy="230 + yellowPupil.y" r="3.5" fill="#333"/>
        <!-- Mouth -->
        <path 
          v-if="!isLookingAtEachOther" 
          d="M388 255 L412 255" 
          stroke="#333" 
          stroke-width="2" 
          stroke-linecap="round"
        />
        <path 
          v-else 
          d="M385 258 Q400 250 415 258" 
          stroke="#333" 
          stroke-width="2" 
          fill="none"
          stroke-linecap="round"
        />
      </g>

      <!-- Small decorative elements -->
      <g class="floating-decor">
        <circle cx="450" cy="150" r="5" fill="#FF6B6B" class="float-dot d1"/>
        <circle cx="50" cy="180" r="4" fill="#4D96FF" class="float-dot d2"/>
        <circle cx="470" cy="250" r="6" fill="#9775FA" class="float-dot d3"/>
        <circle cx="30" cy="300" r="5" fill="#6BCB77" class="float-dot d4"/>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

interface Props {
  isTyping?: boolean
  showPassword?: boolean
  passwordLength?: number
}

const props = withDefaults(defineProps<Props>(), {
  isTyping: false,
  showPassword: false,
  passwordLength: 0,
})

const wrapperRef = ref<HTMLElement | null>(null)
const mouseX = ref(250)
const mouseY = ref(200)

const isLookingAtEachOther = ref(false)
const isPurplePeeking = ref(false)

// Vertical positions for bounce animations
const orangeY = ref(0)
const purpleY = ref(0)
const blackY = ref(0)
const yellowY = ref(0)

let lookTimer: ReturnType<typeof setTimeout> | null = null
let peekTimer: ReturnType<typeof setTimeout> | null = null
let idleTimer: ReturnType<typeof setTimeout> | null = null

// ─── Mouse tracking ─────────────────────────────────────────────────────────
const handleMouseMove = (e: MouseEvent) => {
  if (!wrapperRef.value) return
  const rect = wrapperRef.value.getBoundingClientRect()
  mouseX.value = e.clientX - rect.left
  mouseY.value = e.clientY - rect.top
}

// ─── Computed states ────────────────────────────────────────────────────────
const isHidingPassword = computed(() => props.passwordLength > 0 && !props.showPassword)

// ─── Pupil positions based on mouse ─────────────────────────────────────────
const calculatePupilOffset = (centerX: number, centerY: number) => {
  const deltaX = mouseX.value - centerX
  const deltaY = mouseY.value - centerY
  
  const maxDistance = 3
  const distance = Math.min(Math.sqrt(deltaX ** 2 + deltaY ** 2), 30)
  const angle = Math.atan2(deltaY, deltaX)
  
  const x = Math.cos(angle) * Math.min(distance / 10, maxDistance)
  const y = Math.sin(angle) * Math.min(distance / 10, maxDistance)
  
  return { x, y }
}

const orangePupil = computed(() => {
  if (isHidingPassword.value) return { x: 0, y: 2 }
  return calculatePupilOffset(100, 280)
})

const purplePupil = computed(() => {
  if (isHidingPassword.value) return { x: 0, y: 3 }
  if (isLookingAtEachOther.value) return { x: 5, y: 0 }
  return calculatePupilOffset(195, 200)
})

const blackPupil = computed(() => {
  if (isHidingPassword.value) return { x: 0, y: 4 }
  if (isLookingAtEachOther.value) return { x: -3, y: 0 }
  return calculatePupilOffset(300, 170)
})

const yellowPupil = computed(() => {
  if (isLookingAtEachOther.value) return { x: -5, y: 0 }
  return calculatePupilOffset(400, 230)
})

// ─── Idle bounce animation ───────────────────────────────────────────────────
const startIdleAnimation = () => {
  const bounce = () => {
    const offset = Math.sin(Date.now() / 1000) * 3
    blackY.value = offset
    
    setTimeout(() => {
      orangeY.value = Math.sin(Date.now() / 1200 + 1) * 2
    }, 200)
    
    setTimeout(() => {
      purpleY.value = Math.sin(Date.now() / 1100 + 2) * 2
    }, 400)
    
    setTimeout(() => {
      yellowY.value = Math.sin(Date.now() / 1300 + 3) * 2
    }, 600)
    
    idleTimer = setTimeout(bounce, 50)
  }
  bounce()
}

// ─── Looking at each other effect ──────────────────────────────────────────
watch(() => props.isTyping, (typing) => {
  if (lookTimer) clearTimeout(lookTimer)
  
  if (typing) {
    isLookingAtEachOther.value = true
    // Small bounce
    purpleY.value = -5
    blackY.value = -8
    setTimeout(() => {
      purpleY.value = 0
      blackY.value = 0
    }, 300)
    
    lookTimer = setTimeout(() => {
      isLookingAtEachOther.value = false
    }, 1000)
  }
})

// ─── Purple peeking when password visible ──────────────────────────────────
watch(() => [props.passwordLength, props.showPassword], () => {
  if (peekTimer) clearTimeout(peekTimer)
  
  if (props.passwordLength > 0 && props.showPassword) {
    const schedulePeek = () => {
      peekTimer = setTimeout(() => {
        isPurplePeeking.value = true
        purpleY.value = -10
        setTimeout(() => {
          isPurplePeeking.value = false
          purpleY.value = 0
        }, 600)
        schedulePeek()
      }, Math.random() * 2500 + 2000)
    }
    schedulePeek()
  } else {
    isPurplePeeking.value = false
  }
}, { immediate: true })

// ─── Hiding password animation ──────────────────────────────────────────────
watch(isHidingPassword, (hiding) => {
  if (hiding) {
    // Shake/shy animation
    purpleY.value = -5
    blackY.value = -8
    setTimeout(() => {
      purpleY.value = 3
      blackY.value = 5
    }, 150)
    setTimeout(() => {
      purpleY.value = 0
      blackY.value = 0
    }, 300)
  }
})

// ─── Lifecycle ─────────────────────────────────────────────────────────────
onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
  startIdleAnimation()
  mouseX.value = 250
  mouseY.value = 200
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  if (lookTimer) clearTimeout(lookTimer)
  if (peekTimer) clearTimeout(peekTimer)
  if (idleTimer) clearTimeout(idleTimer)
})
</script>

<style scoped>
.characters-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.characters-svg {
  width: 100%;
  max-width: 500px;
  height: auto;
}

.character-body {
  transition: fill 0.3s ease;
}

/* Floating dots animation */
.float-dot {
  animation: floatUp 3s ease-in-out infinite;
}

.d1 { animation-delay: 0s; }
.d2 { animation-delay: 0.5s; }
.d3 { animation-delay: 1s; }
.d4 { animation-delay: 1.5s; }

@keyframes floatUp {
  0%, 100% { transform: translateY(0); opacity: 0.6; }
  50% { transform: translateY(-10px); opacity: 1; }
}

/* Main character special glow */
.main-character {
  filter: drop-shadow(0 4px 20px rgba(0, 0, 0, 0.3));
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .float-dot,
  g {
    animation: none !important;
    transition: none !important;
  }
}
</style>
