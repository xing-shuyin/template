<template>
    <div>
        <el-cascader-panel class="iconify-icon-panel" v-model="model" :props="props" filterable>
            <template #default="{ node, data }">
                <div class="iconify-icon-panel-item">
                    <div class="iconify-icon-panel-item-label" :title="data.label">{{ data.label }}</div>
                    <Icon v-if="node.isLeaf" :icon="data.value" class="btn-icon" />
                </div>

            </template>

        </el-cascader-panel>
    </div>
</template>

<script setup>
import { Icon } from '@iconify/vue'
import r from '@/utils/request'
const attrs = reactive({
    icons: [],
});
const props = {
    lazy: true,
    lazyLoad(node, resolve) {
        if (node.level === 0) {
            r.get('/iconify_collections/').then(res => {
                console.log('collections:', res);
                res = res.data
                let temp = []
                for (let i in res) {
                    temp.push({ 'value': i, 'label': res[i].name || i })
                }
                console.log('collections temp:', temp);
                resolve(temp)
            }).catch(err => {
                console.error('加载图标集合失败:', err);
                resolve([])
            })
        } else if (node.level === 1) {
            r.get('/iconify_icons/', { params: { prefix: node.value } }).then(res => {
                console.log('icons:', res);
                res = res.data
                let temp = []
                if (res.hasOwnProperty("categories")) {
                    for (let i in res.categories) {
                        let temp2 = []
                        res.categories[i].forEach((item) => {
                            temp2.push({ 'value': node.value + ':' + item, 'label': node.value + ':' + item, leaf: true, prefix: node.value })
                        })
                        temp.push({ 'value': i, 'label': i, children: temp2 })
                    }
                }
                if (res.hasOwnProperty("uncategorized") && res.uncategorized.length > 0) {
                    res.uncategorized.forEach((item) => {
                        temp.push({ 'value': node.value + ':' + item, 'label': node.value + ':' + item, leaf: true, prefix: node.value })
                    })
                }
                console.log('icons temp:', temp);
                resolve(temp)
            }).catch(err => {
                console.error('加载图标列表失败:', err);
                resolve([])
            })
        }
    },
    value: 'value',
    label: 'label',
    children: 'children',
    checkStrictly: false,
    emitPath: false,
    multiple: false,
    collapseTags: true,
    filterable: true,
};
const model = defineModel()

</script>

<style lang="scss">
.iconify-icon-panel {
    .el-cascader-node__label {
        white-space: wrap;
    }

    .iconify-icon-panel-item {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;

        .iconify-icon-panel-item-label {
            // 字数限制
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 200px;
        }
    }
}
</style>
