<template>
    <div class="main">
        <!-- 搜索 / 过滤栏 -->
        <div class="main-top">
            <div class="search">
                <f-input v-model="filter.name__contains" label="名称" placeholder="对话名称模糊搜索" />
                <f-input v-model="filter.model__contains" label="模型" placeholder="按模型搜索" />
            </div>
            <div class="tool">
                <el-button circle @click="add">
                    <Icon icon="ep:plus" class="btn-icon" />
                </el-button>
                <f-columns-edit v-if="attrs.columns" v-model="attrs.columns" :base_url="attrs.base" />
            </div>
        </div>

        <!-- 数据表格 -->
        <div class="main-table">
            <el-table :data="attrs.data" style="width:100%;height:100%" stripe @sort-change="onSortChange">
                <columns :columns="attrs.columns" />
                <el-table-column label="操作" width="120" align="center" fixed="right">
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

        <!-- 分页 -->
        <div class="main-foot">
            <el-pagination background layout="total, prev, pager, next" hide-on-single-page style="margin:5px"
                :total="attrs.total" :page-sizes="[10, 20, 30, 50]" v-model:page-size="filter.limit"
                v-model:current-page="filter.page" />
        </div>

        <!-- 编辑对话框 -->
        <el-dialog class="admin_detail_dialog" :class="store().theme" v-model="attrs.current_show"
            :title="attrs.current_type === 'add' ? '新增对话' : '编辑对话'" :append-to-body="false" :show-close="false"
            destroy-on-close width="720px">
            <el-form :model="attrs.current" label-width="100px" ref="formRef" :rules="rules">
                <el-form-item label="对话名称" prop="name">
                    <el-input v-model="attrs.current.name" placeholder="自动由首条消息生成" />
                </el-form-item>
                <el-form-item label="模型" prop="model">
                    <el-input v-model="attrs.current.model" placeholder="模型名称" />
                </el-form-item>
                <el-form-item label="角色 ID" prop="role_id">
                    <el-input-number v-model="attrs.current.role_id" :min="0" :value-on-clear="null" style="width:100%" />
                </el-form-item>
                <el-form-item label="Token 数" prop="tokens_used">
                    <el-input-number v-model="attrs.current.tokens_used" :min="0" style="width:100%" />
                </el-form-item>
                <el-form-item label="消息内容">
                    <el-input v-model="messagesText" type="textarea" :rows="12"
                        placeholder="JSON 格式，每条消息一行" />
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
    base: 'chat',
    data: [],
    total: 0,
    current: {},
    current_show: false,
    current_type: 'add',
    columns: [
        { type: 'text',   width: 200, label: '名称',      prop: 'name',         align: 'center', show: true, sortable: true },
        { type: 'text',   width: 120, label: '模型',      prop: 'model',        align: 'center', show: true },
        { type: 'number', width: 80,  label: '角色 ID',   prop: 'role_id',      align: 'center', show: true },
        { type: 'number', width: 80,  label: '消息数',    prop: 'msg_count',    align: 'center', show: true },
        { type: 'number', width: 80,  label: 'Token',     prop: 'tokens_used',  align: 'center', show: true },
        { type: 'utc',    width: 170, label: '最后消息',  prop: 'last_message_at', align: 'center', show: true, sortable: true },
        { type: 'utc',    width: 170, label: '创建时间',  prop: 'created_at',   align: 'center', show: true, sortable: true },
        { type: 'utc',    width: 170, label: '更新时间',  prop: 'updated_at',   align: 'center', show: true, sortable: true },
    ],
})

const formRef = ref(null)
const rules = reactive({
    name: [{ required: false, message: '', trigger: 'blur' }],
})

const filter = reactive({
    limit: 10,
    page: 1,
})

watch(filter, () => { get_data() }, { deep: true })

// 消息内容文本（JSON 序列化/反序列化）
const messagesText = computed({
    get: () => {
        const msgs = attrs.current.messages || []
        return msgs.map(m => JSON.stringify(m, null, 2)).join('\n\n---\n\n')
    },
    set: (val) => {
        try {
            const parts = val.split(/\n---\n/)
            attrs.current.messages = parts.map(p => JSON.parse(p.trim()))
        } catch {
            // 暂不处理，提交时校验
        }
    }
})

/* ─── 操作 ─── */

const onSortChange = (d) => {
    if (d.order === 'ascending')          filter.order = d.prop
    else if (d.order === 'descending')    filter.order = '-' + d.prop
    else                                  delete filter.order
}

const add = () => {
    attrs.current = { name: '', model: '', role_id: null, messages: [], tokens_used: 0 }
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
    delete payload.msg_count

    // 验证 messages JSON
    if (payload.messages && typeof payload.messages === 'string') {
        try {
            payload.messages = JSON.parse(payload.messages)
        } catch {
            ElMessage({ message: '消息内容不是有效的 JSON', type: 'warning', center: true })
            return
        }
    }

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
        attrs.data = (body.data || []).map(item => ({
            ...item,
            msg_count: (item.messages || []).length,
        }))
        attrs.total = parseInt(body.total) || 0
    })
}

get_data()
</script>

<style lang="scss" scoped>
</style>
