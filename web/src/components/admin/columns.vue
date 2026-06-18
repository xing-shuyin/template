<template>
    <!--
    columns 配置说明：

    type      说明                    必需字段                                   可选字段
    ─────────────────────────────────────────────────────────────────────────────────
    text      纯文本显示              prop, label                                —
    select    映射标签                prop, label, option(字典 {val: name})       —
    dict_dict 嵌套字典取值            prop, label, option(字典 {val: {}})         key(子字段,默认name)
    list_dict 字典数组→多个标签       prop, label, option(字典 {val: {}})         key(子字段,默认name)
    list      字符串数组→多个标签     prop, label                                —
    list_item 数字数组→映射多个标签   prop, label, option(字典 {id: name})        —
    bool      是/否标签              prop, label                                —
    jfile     文件链接列表            prop, label                                —
    jimage    图片预览                prop, label                                imageSrc(scope→url函数)
    link      超链接                  prop, label                                —
    utc       UTC转本地时间           prop, label                                —
    file      下载文件                prop, label                                —
    iconify   Iconify图标             prop, label                                —

    通用字段: show(默认true), width, align, sortable, overflow(默认true)
    -->
    <template v-for="i in columns" :key="i.prop">
        <!-- 普通文本 -->
        <el-table-column v-if="i.type == 'text' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <span>{{ scope.row[i.prop] }}</span>
            </template>
        </el-table-column>
        <!-- 单选用标签 -->
        <el-table-column v-else-if="i.type == 'select' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <el-tag effect="dark" class="scope_tag">
                    {{ i.option[scope.row[i.prop]] }}
                </el-tag>
            </template>
        </el-table-column>
        <!-- 字典套字典 -->
        <el-table-column v-else-if="i.type == 'dict_dict' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <el-tag effect="dark" class="scope_tag">
                    {{ i.option[scope.row[i.prop]]?.[i.key || 'name'] }}
                </el-tag>
            </template>
        </el-table-column>
        <!-- 字典列表 -->
        <el-table-column v-else-if="i.type == 'list_dict' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <el-tag effect="dark" v-for="v in scope.row[i.prop]" :key="v" class="scope_tag">
                    {{ i.option[v]?.[i.key || 'name'] }}
                </el-tag>
            </template>
        </el-table-column>
        <!-- 列表 -->
        <el-table-column v-else-if="i.type == 'list' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <el-tag effect="dark" v-for="v in scope.row[i.prop]" :key="v" class="scope_tag">
                    {{ v }}
                </el-tag>
            </template>
        </el-table-column>
        <!-- 列表映射 -->
        <el-table-column v-else-if="i.type == 'list_item' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <el-tag effect="dark" v-for="v in scope.row[i.prop]" :key="v" class="scope_tag">
                    {{ i.option[v] }}
                </el-tag>
            </template>
        </el-table-column>
        <!-- bool -->
        <el-table-column v-else-if="i.type == 'bool' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <el-tag effect="dark" class="scope_tag">
                    {{ scope.row[i.prop] ? '是' : '否' }}
                </el-tag>
            </template>
        </el-table-column>
        <!-- 文件列表 -->
        <el-table-column v-else-if="i.type == 'jfile' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <div class="form-files">
                    <div v-for="(f, fi) in scope.row[i.prop]" :key="fi">
                        <a :href="f.url" target="_blank">{{ f.name }}</a>
                    </div>
                </div>
            </template>
        </el-table-column>
        <!-- 图片 -->
        <el-table-column v-else-if="i.type == 'jimage' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <el-image v-if="scope.row[i.prop]?.[0]" style="width: 70px; height: 70px" fit="cover" :z-index="30"
                    :src="i.imageSrc?.(scope.row) || scope.row[i.prop][0]?.url"
                    :preview-src-list="scope.row[i.prop].map(f => f.url)"
                    preview-teleported hide-on-click-modal />
            </template>
        </el-table-column>
        <!-- 链接 -->
        <el-table-column v-else-if="i.type == 'link' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <a :href="scope.row[i.prop]" target="_blank">{{ scope.row[i.prop] }}</a>
            </template>
        </el-table-column>
        <!-- utc时间转本地时间 -->
        <el-table-column v-else-if="i.type == 'utc' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <span>{{ utc_to_local(scope.row[i.prop]) }}</span>
            </template>
        </el-table-column>
        <!-- 文件下载 -->
        <el-table-column v-else-if="i.type == 'file' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <a :href="`/api/download/${scope.row.id}`" target="_blank">{{ scope.row[i.prop] }}</a>
            </template>
        </el-table-column>
        <!-- 图标 -->
        <el-table-column v-else-if="i.type == 'iconify' && i.show" v-bind="getColumnConfig(i)">
            <template #default="scope">
                <Icon :icon="scope.row[i.prop]" class="btn-icon" />
            </template>
        </el-table-column>
    </template>
</template>
<script setup>
import { Icon } from '@iconify/vue';
import { utc_to_local } from '@/utils/tool'

const props = defineProps({
    columns: {
        type: Array,
        required: true,
    }
})

const getColumnConfig = (i) => {
    return {
        align: i.align || 'center',
        label: i.label || '',
        key: i.prop || '',
        prop: i.prop || '',
        sortable: i.sortable || false,
        width: i.width || '',
        'show-overflow-tooltip': i?.overflow ?? true,
    };
}
</script>
<style scoped lang="scss">
.scope_tag {
    margin: 3px;
}
</style>
