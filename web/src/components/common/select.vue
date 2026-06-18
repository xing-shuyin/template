<template>
    <div class="common-select">
        <div class="common-select-current" @click.stop="attrs.show = !attrs.show">

            {{ current.label }}
        </div>
        <div class="common-select-options" v-show="attrs.show">
            <div class="common-select-option" v-for="option in options" :key="option.id" @click="model = option.id">
                {{ option.label }}({{ option.type }})
            </div>
        </div>

    </div>
</template>
<script setup>
const model = defineModel();
const props = defineProps(['options']);
const attrs = reactive({
    show: false,
});
const current = computed(() => {
    // 使用 model.value 而不是直接 model
    let r = props.options.find(i => String(i.id) === String(model.value))
    if (r) {
        return r
    } else {
        return { name: '未选择', type: '未选择' }
    }
});
window.addEventListener('click', () => {
    attrs.show = false;
})
</script>
<style lang="scss" scoped>
.common-select {
    text-align: left;

    .common-select-current {
        box-sizing: border-box;
        height: 40px;
        width: min-content;
        border-radius: 8px;
        color: #b4b4b4;
        padding: 6px 12px;
        margin: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-family: 600;
        user-select: none;
        background-color: #2f2f2f;
        white-space: nowrap;
    }

    .common-select-current:hover {
        background-color: rgba(0, 0, 0, 0.315);
    }

    .common-select-options {
        // padding: 8px;
        transition-duration: 100ms;
        box-sizing: border-box;
        margin: 8px;
        width: 300px;
        border-radius: 16px;
        background-color: #2f2f2f;
        display: flex;
        flex-direction: column;


        .common-select-option {
            box-sizing: border-box;
            height: 40px;

            border-radius: 8px;
            color: #b4b4b4;
            padding: 6px 12px;
            margin: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-family: 600;
            user-select: none;
            white-space: nowrap;
        }

        .common-select-option:hover {
            background-color: rgba(255, 255, 255, 0.116);
        }

    }
}
</style>