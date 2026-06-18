<template>
    <div ref="editor" id="jsonview">

    </div>
</template>
<script setup>
import { onBeforeUnmount, onMounted, watch } from 'vue';
import 'jsoneditor/dist/jsoneditor.css'
import JSONEditor from 'jsoneditor'
const model = defineModel();
const editor = ref(null)
onMounted(() => {
    const container = document.getElementById('jsonview');
    const options = {
        // 这里可以设置你需要的选项
        mode: 'view',
        mainMenuBar: false,
        navigationBar: false,
        statusBar: false,
    }
    editor.value = new JSONEditor(container, options)
    editor.value.set(model.value)
})
onBeforeUnmount(() => {
    editor.value.destroy()
})
</script>
<style scoped lang='scss'>
#jsonview {
    min-width: 500px;
    // min-height: 500px;
    font-family: '宋体';
}
</style>
