<!-- VisibleObserver.vue -->
<template>
    <div ref="targetRef">
        <slot />
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
    on_show: {
        type: Function,
        required: true
    },
    threshold: {
        type: [Number, Array],
        default: 0.1 // 默认 10% 可见即视为“出现”
    },
    rootMargin: {
        type: String,
        default: '0px'
    }
})

const targetRef = ref(null)
let observer = null

onMounted(() => {
    observer = new IntersectionObserver((entries) => {
        for (const entry of entries) {
            if (entry.isIntersecting) {
                // 每次进入视口都触发
                console.log('2222222222');
                props.on_show()
            }
            // 注意：不调用 unobserve，保持持续监听
        }
    }, {
        threshold: props.threshold,
        rootMargin: props.rootMargin
    })

    if (targetRef.value) {
        observer.observe(targetRef.value)
    }
})

onUnmounted(() => {
    if (observer) {
        observer.disconnect()
    }
})
</script>