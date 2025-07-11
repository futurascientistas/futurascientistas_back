import axios from "axios";

const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL, // API interna do Next.js (proxy que injeta o token)
  withCredentials: true, // envia cookies (ex: token HttpOnly)
});

export default axiosInstance;
