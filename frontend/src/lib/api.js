import axios from 'axios'
export const api=axios.create({baseURL:import.meta.env.VITE_API_URL||'http://localhost:8000'})
api.interceptors.request.use(c=>{const t=localStorage.getItem('sp_token');if(t)c.headers.Authorization=`Bearer ${t}`;return c})
export const wsBase=(import.meta.env.VITE_WS_URL||'ws://localhost:8000')
