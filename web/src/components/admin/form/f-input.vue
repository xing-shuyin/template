<script setup>
const model = defineModel()
const props = defineProps(['label', 'placeholder', 'size']); // defineProps的参数, 可以直接使用
// 防抖输入框
const temp = ref(undefined)
const update_value = () => {
    model.value = temp.value
}
</script>
<template>
    <el-form-item :label="label" :size="size">
        <el-input v-model="temp" :placeholder="placeholder" clearable style="width: 100px;" @blur="update_value()"
            :size="size" @keyup.enter="update_value()" @clear="temp = undefined; update_value()">
        </el-input>
    </el-form-item>
</template>
<style scoped lang='scss'></style>
