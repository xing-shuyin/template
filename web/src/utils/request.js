// src/utils/request.js
import axios from 'axios';
import bus from '@/utils/bus'
// 创建一个 Axios 实例
const service = axios.create({
  baseURL: import.meta.env.VITE_BASE_API || '/', // 基础路径，支持从环境变量中获取
  timeout: 5000, // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 可在此处添加token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    config.withCredentials = true; // 携带cookie

    return config;
  },
  (error) => {
    // 请求错误处理
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    return response
    // const res = response.data;
    // // 根据业务处理响应数据
    // console.log(typeof res, typeof res === 'Object');
    // if (typeof res === 'Object') {
    //   console.log(response.status);
    //   res.status = response.status;
    // }
    // return res;
  },
  (error) => {
    // 响应错误处理
    bus.emit('response:error', error);
    return Promise.reject(error);
  }
);


export const CURD = (model) => {
  return {
    list: (params) => service.get(`/${model}/`, { params: params }),
    create: (data) => service.post(`/${model}/`, data),
    update: (id, data) => service.patch(`/${model}/${id}/`, data),
    delete: (id) => service.delete(`/${model}/${id}/`),
  }
}

export default service;
