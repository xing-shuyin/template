<template>
    <div class="main">
        <div class="main-top">
            <div class="search">
                <f-input v-model="filter.name__contains" label="名称" placeholder="搜索模型名称" />
                <el-form-item label="类型">
                    <el-select v-model="filter.type" placeholder="全部" clearable style="width:110px" @change="get_data">
                        <el-option label="全部" value="" />
                        <el-option label="OpenAI" value="openai" />
                        <el-option label="DeepSeek" value="deepseek" />
                        <el-option label="Anthropic" value="anthropic" />
                    </el-select>
                </el-form-item>
            </div>
            <div class="tool">
                <el-button circle @click="add">
                    <Icon icon="ep:plus" class="btn-icon" />
                </el-button>
                <f-columns-edit v-if="attrs.columns" v-model="attrs.columns" :base_url="attrs.base" />
            </div>
        </div>
        <div class="main-table">
            <el-table :data="attrs.data" style="width:100%;height:100%" stripe @sort-change="sort">
                <columns :columns="attrs.columns" />
                <el-table-column label="操作" width="180" align="center" fixed="right">
                    <template #default="scope">
                        <el-button type="primary" link @click="edit(scope.row)">编辑</el-button>
                        <el-popconfirm title="确定删除吗?" @confirm="del(scope.row)">
                            <template #reference>
                                <el-button type="danger" link>删除</el-button>
                            </template>
                        </el-popconfirm>
                    </template>
                </el-table-column>
            </el-table>
        </div>
        <div class="main-foot">
            <el-pagination background layout="total, prev, pager, next" hide-on-single-page style="margin:5px"
                :total="attrs.total" :page-sizes="[10, 20, 30, 50]" v-model:page-size="filter.limit"
                v-model:current-page="filter.page" />
        </div>

        <!-- 新增/编辑对话框 -->
        <el-dialog class="admin_detail_dialog" :class="store().theme" v-model="attrs.current_show"
            :title="attrs.current_type === 'add' ? '新增模型' : '编辑模型'" :append-to-body="false" :show-close="false"
            destroy-on-close width="560px">
            <el-form :model="attrs.current" label-width="120px" ref="formRef" :rules="rules">
                <el-form-item label="模型名称" prop="name">
                    <el-input v-model="attrs.current.name" placeholder="例: gpt-4o-mini" />
                </el-form-item>
                <el-form-item label="显示名称" prop="label">
                    <el-input v-model="attrs.current.label" placeholder="例: GPT-4o-mini" />
                </el-form-item>
                <el-form-item label="提供商" prop="type">
                    <el-select v-model="attrs.current.type" placeholder="选择类型" style="width:100%">
                        <el-option label="OpenAI 兼容" value="openai" />
                        <el-option label="Anthropic" value="anthropic" />
                        <el-option label="DeepSeek" value="deepseek" />
                    </el-select>
                </el-form-item>
                <el-form-item label="API 地址" prop="base_url">
                    <el-input v-model="attrs.current.base_url" placeholder="https://api.openai.com/v1" />
                </el-form-item>
                <el-form-item label="API Key" prop="api_key">
                    <el-input v-model="attrs.current.api_key" type="password" show-password
                        placeholder="sk-..." />
                </el-form-item>
                <el-form-item label="功能">
                    <el-checkbox v-model="attrs.current.vision">视觉识别</el-checkbox>
                    <el-checkbox v-model="attrs.current.tools" style="margin-left:16px">工具调用</el-checkbox>
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="attrs.current_show = false">取消</el-button>
                    <el-button type="primary" @click="validate">提交</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import r from '@/utils/request'
import store from '@/utils/store'
import { Icon } from '@iconify/vue'

const attrs = reactive({
    base: 'model',
    data: [],
    current: {},
    current_show: false,
    current_type: 'add',
    total: 0,
    columns: [
        { type: 'text', width: 180, label: '名称',      prop: 'name',       align: 'center', show: true, sortable: true },
        { type: 'text', width: 180, label: '显示名称',  prop: 'label',      align: 'center', show: true },
        { type: 'text', width: 100, label: '提供商',    prop: 'type',       align: 'center', show: true },
        { type: 'text', width: 280, label: 'API 地址',  prop: 'base_url',   align: 'center', show: true },
        { type: 'bool', width: 80,  label: '视觉',      prop: 'vision',     align: 'center', show: true },
        { type: 'bool', width: 80,  label: '工具',      prop: 'tools',      align: 'center', show: true },
        { type: 'utc',  width: 170, label: '创建时间',  prop: 'created_at', align: 'center', show: true, sortable: true },
    ]
})

const formRef = ref(null)
const rules = reactive({
    name:  [{ required: true, message: '请填写模型名称', trigger: 'blur' }],
    label: [{ required: true, message: '请填写显示名称', trigger: 'blur' }],
    type:  [{ required: true, message: '请选择提供商',   trigger: 'change' }],
})

const filter = reactive({
    limit: 30,
    page: 1,
})

watch(filter, () => { get_data() }, { deep: true })

const sort = (d) => {
    if (d.order === 'ascending')          filter.order = d.prop
    else if (d.order === 'descending')    filter.order = '-' + d.prop
    else                                  delete filter.order
}

const add = () => {
    attrs.current = { vision: false, tools: false, type: 'openai' }
    attrs.current_type = 'add'
    attrs.current_show = true
}

const edit = (row) => {
    attrs.current = { ...row }
    attrs.current_type = 'edit'
    attrs.current_show = true
}

const del = (row) => {
    r.delete(`/${attrs.base}/${row.id}`).then(res => {
        if (res.status === 200) {
            ElMessage({ message: '删除成功', type: 'success', plain: true })
            get_data()
        }
    })
}

const validate = () => {
    formRef.value.validate((valid, fields) => {
        if (valid) submit()
        else ElMessage({ showClose: true, message: Object.values(fields)[0][0].message, center: true })
    })
}

const submit = () => {
    const payload = { ...attrs.current }
    delete payload.created_at
    delete payload.updated_at

    if (attrs.current_type === 'add') {
        delete payload.id
        delete payload.creator_id
        r.post(`/${attrs.base}/`, payload).then(res => {
            if (res.status === 200) {
                ElMessage({ message: '添加成功', type: 'success', plain: true })
                attrs.current_show = false
                get_data()
            }
        })
    } else {
        r.patch(`/${attrs.base}/${attrs.current.id}`, payload).then(res => {
            if (res.status === 200) {
                ElMessage({ message: '修改成功', type: 'success', plain: true })
                attrs.current_show = false
                get_data()
            }
        })
    }
}

const get_data = () => {
    attrs.data = []
    r.get(`/${attrs.base}/`, { params: filter }).then(res => {
        const body = res.data
        attrs.data = body.data || []
        attrs.total = parseInt(body.total) || 0
    })
}
get_data()
</script>

<style lang="scss" scoped></style>
