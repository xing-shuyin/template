<template>
    <el-pagination class="pager" v-model:currentPage="attrs.page" v-model:page-size="attrs.limit" :background="true"
        :page-sizes="[50, 100, 200, 300, 400]" layout="total, sizes, prev, pager, next, jumper" :total="total"
        :pager-count="11">
    </el-pagination>
</template>
<script setup>
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { onBeforeMount } from 'vue';
const props = defineProps(['page', 'limit', 'total']); // defineProps的参数, 可以直接使用
const emits = defineEmits(['update:page', 'update:limit']); // emits 触发父组件函数
const attrs = reactive({
    page: 1,
    limit: 10,
})
onBeforeMount(() => {
    attrs.page = props.page
    attrs.limit = props.limit
})
watch(() => attrs.page, () => {
    emits('update:page', attrs.page)
})
watch(() => attrs.limit, () => {
    emits('update:limit', attrs.limit)
})
</script>
<style scoped lang='scss'></style>
