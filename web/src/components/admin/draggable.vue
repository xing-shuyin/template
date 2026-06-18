<template>
    <div ref="sortableContainer" class="sortable-container">
        <div v-for="(item, index) in model" :key="item[item_key]" class="sortable-item">
            <slot name="item" v-bind="{ item, index }"></slot>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Sortable from 'sortablejs';
const model = defineModel()
const props = defineProps(['item_key']);
const sortableContainer = ref(null);
onMounted(() => {
    // 使用 sortablejs 初始化排序
    new Sortable(sortableContainer.value, {
        onEnd(evt) {
            // 当排序结束时，更新父组件的数据
            const movedItem = model.value.splice(evt.oldIndex, 1)[0];
            model.value.splice(evt.newIndex, 0, movedItem);
        },
    });
})
defineExpose({
    sortableContainer,
})
</script>

<style scoped>
.sortable-container {
    display: flex;
    flex-direction: column;
}

.sortable-item {
    margin: 5px 0;
}
</style>
