<!-- 
modelValue = ref([
    { type: 'text', label: '名称', prop: 'name', size: 'small', align: "left", show: true },
    { type: 'select', width: 180, label: '角色', prop: 'role', size: 'small', align: "center", show: true },
    { type: 'jimage', width: 150, label: '图片', prop: 'user_image', size: 'small', align: "center", show: true, option: { false: '否', true: '是' } },
    { type: 'jfile', width: 160, label: '文件', prop: 'file', size: 'small', align: "center", show: true },
])
 -->
<script setup>
//TODO:列编辑
import { Icon } from '@iconify/vue';  //https://www.npmjs.com/package/@iconify/vue
const model = defineModel()
const props = defineProps(['base_url']); // defineProps的参数, 可以直接使用
const attrs = reactive({
    drag: false,
    columns: [],
    show: false,
})
let columns;
onBeforeMount(() => {
    let temp = []
    for (let index = 0; index < model.value.length; index++) {
        temp.push({ ...model.value[index] })
    }
    columns = temp
    if (localStorage.getItem(`columns_${props.base_url}`)) {
        attrs.columns = JSON.parse(localStorage.getItem(`columns_${props.base_url}`))
    } else {
        attrs.columns = model.value
    }
})

watch(() => { return attrs.columns }, () => {
    localStorage.setItem(`columns_${props.base_url}`, JSON.stringify(attrs.columns))
    model.value = attrs.columns
}, { deep: true })
const reset_column = () => {
    let temp = []
    for (let index = 0; index < columns.length; index++) {
        temp.push({ ...columns[index] })
    }
    attrs.columns = temp
}
</script>
<template>
    <el-button circle @click="attrs.show = true;">
        <Icon icon="ep:operation" class="btn-icon" />
    </el-button>
    <!-- 编辑列 -->
    <el-drawer v-model="attrs.show" size="680px" center append-to-body :modal="true" :show-close="false">
        <template v-slot:header>
            <span style="font-size: 16px;">
                编辑列(拖动以修改顺序)
            </span>
            <el-tooltip content="重置" placement="bottom" effect="light">
                <el-button style="position: absolute;right: 17px;" circle @click="reset_column">
                    <Icon icon="ep:refresh" class="btn-icon" />
                </el-button>
            </el-tooltip>

        </template>
        <draggable v-model="attrs.columns" item_key="label">
            <template #item="item">
                <div class="column-manager-line">
                    <table>
                        <tbody>
                            <tr>
                                <td>{{ item.index + 1 }}</td>
                                <td style="width: 30px;"><el-switch v-model="item.item.show" inline-prompt /></td>
                                <td style="width: 150px;">
                                    <el-input v-model="item.item.label" placeholder="列名" />
                                </td>
                                <td style="width: 20px;"><el-input-number v-model="item.item.width" :min="1" :max="500"
                                        controls-position="right" />
                                </td>
                                <td style="width: 120px;">
                                    <el-radio-group v-model="item.item.align" size="small">
                                        <el-radio-button key="left" value="left">左</el-radio-button>
                                        <el-radio-button key="center" value="center">中</el-radio-button>
                                        <el-radio-button key="right" value="right">右</el-radio-button>
                                    </el-radio-group>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </template>
        </draggable>
    </el-drawer>
</template>
<style scoped lang='scss'>
.column-manager-line {
    background-color: var(--admin-main-column-edit-line-bg);
    border-radius: 10px;
    margin-bottom: 3px;

    table {
        tr {
            td {
                width: 70px;
                padding: 3px;
                text-align: center;
            }
        }
    }
}
</style>
