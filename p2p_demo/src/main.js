import { io } from "socket.io-client";
import { createApp } from "vue"
import { createPinia } from "pinia";
import VNetworkGraph from "v-network-graph";
import "v-network-graph/lib/style.css";
import App from "./App.vue";

const sio = io("http://127.0.0.1:8000");

const app = createApp(App)
app.use(createPinia());
app.use(VNetworkGraph);
app.provide('socket', sio);
app.mount("#app")
