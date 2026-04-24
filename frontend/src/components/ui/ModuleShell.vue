<template>
  <component
    :is="as"
    class="glass-card module-shell"
    :class="[
      `module-shell--${accent}`,
      { 'module-shell-interactive': interactive },
    ]"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  as?: 'section' | 'article' | 'div'
  accent?: 'cyan' | 'green' | 'gold' | 'red'
  interactive?: boolean
}>(), {
  as: 'section',
  accent: 'cyan',
  interactive: false,
})
</script>
