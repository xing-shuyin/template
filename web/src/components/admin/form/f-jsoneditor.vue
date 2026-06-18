<template>
    <div ref="editor" id="jsoneditor">

    </div>
</template>
<script setup>
import JSONEditor from 'jsoneditor'
import 'jsoneditor/dist/jsoneditor.css'
import { onBeforeUnmount, onMounted, watch } from 'vue';
const model = defineModel();
const attrs = reactive({ editor: null });


const editor = ref(null)
onMounted(() => {
    const container = document.getElementById('jsoneditor');
    attrs.editor = new JSONEditor(container, {
        modes: ['code', 'tree', 'form'],
        theme: 'dark',
        onChange: function () {
            model.value = attrs.editor.get();
        },
    })
    attrs.editor.set(model.value)
})
onBeforeUnmount(() => {
    attrs.editor.destroy()
})
</script>
<style scoped lang='scss'>
#jsoneditor {
    width: 100%;
    min-width: 500px;
    height: 500px;
    font-family: '宋体';
}
</style>
