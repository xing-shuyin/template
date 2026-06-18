<template>
    <div class="context-container" ref="menus">
        <slot></slot>
        <teleport to="body">
            <Transition @beforeEnter="handleBeforeEnter" @enter="handleEnter" @afterEnter="handleAfterEnter">
                <div v-if="attrs.show" class="context-menu" :style="{ top: attrs.y + 'px', left: attrs.x + 'px' }"
                    @click.right.stop.prevent="void (0)">
                    <div class="context-menu-item" v-for="i, index in menu" :key="index"
                        @click.self="emits('select', index)">
                        {{ i }}
                    </div>
                </div>
            </Transition>
        </teleport>
    </div>
</template>
<script setup>
import { onBeforeUnmount, onMounted, onUnmounted } from 'vue';
const props = defineProps(['menu']); //子向父传数据
const emits = defineEmits(['select']); //父调用子函数
const menus = ref(null);
const attrs = reactive({
    x: 0,
    y: 0,
    show: false,
});

const show_menu = (e) => {
    e.preventDefault();
    e.stopPropagation();
    attrs.x = e.x;
    attrs.y = e.y;
    attrs.show = true;
}

const close_menu = () => {
    attrs.show = false;
}
const handleBeforeEnter = (e) => {
    e.style.height = '0';
}
const handleEnter = (e) => {
    e.style.height = 'auto';
    const h = e.clientHeight;
    e.style.height = '0';
    requestAnimationFrame(() => {
        e.style.height = h + 'px';
        e.style.transition = '.5s';
    })
}
const handleAfterEnter = (e) => {
    e.style.transition = 'none';
}


onMounted(() => {
    menus.value.addEventListener('contextmenu', show_menu)
    window.addEventListener('click', close_menu, true)
    window.addEventListener('contextmenu', close_menu, true)
})
onBeforeUnmount(() => {
    menus.value.removeEventListener('contextmenu', show_menu)
    window.removeEventListener('contextmenu', close_menu)
    window.removeEventListener('click', close_menu)
})



</script>
<style lang='scss'>
:root {
    --context-menu-bg-color: aliceblue;
    --context-menu-item-hover-bg-color: #ccc;
    --context-menu-item-color: black;
}

.dark {
    --context-menu-bg-color: #333;
    --context-menu-item-hover-bg-color: #555;
    --context-menu-item-color: white;
}

.context-menu {
    background-color: var(--context-menu-bg-color);
    border-radius: 8px;
    padding: 5px;
    position: absolute;
    overflow: hidden;

    .context-menu-item {
        cursor: pointer;
        padding: 3px;
        border-radius: 3px;
        min-width: 80px;
        color: var(--context-menu-item-color);
    }

    .context-menu-item:hover {
        background-color: var(--context-menu-item-hover-bg-color);
    }
}
</style>
