<script setup lang="ts">
	import { inject, onMounted } from 'vue';
	import { useNetworkStore } from '@/stores/network.js';
	import { reactive } from "vue"
	import Legend from "@/Legend.vue"
	import * as vNG from "v-network-graph"
	const socket = inject('socket');
	const network = useNetworkStore();


	function animateEdge(edge_id, message_type) {
	  let color;
	  switch (message_type) {
	    case "REQ": color = "blue"; break;
	    case "REPLY": color = "purple"; break;
	    case "JOB": color = "yellow"; break;
	    case "SUCCESS": color = "green"; break;
	    case "PING": color = "gray"; break;
	    default: color = "black";
	  }
	
	  const edge = network.edges[edge_id];
	  if (!edge) return;
	
	  // In-place reactive update
	  const originalColor = edge.color;
	 edge.color = color;
	
	  setTimeout(() => {
	    edge.color = originalColor;
	  }, 250);
	}

	onMounted(() => {
	  socket.on('node_connect', data => {
			network.addNode(data);
	  });
	
	  socket.on('edge_update', data => {
			console.log('received update')
			const peer_id = data.peer_id;
			const neighbor_set = new Set(data.neighbor_set);
			for ( const neighbor_id of neighbor_set ) {
	    	network.addEdge(peer_id, neighbor_id)
			}
	  });
		
		
		// Component
		socket.on('edge_traffic', data => {
			console.log(JSON.stringify(data))
		  const edge_id = `${data.peer_id}_${data.neighbor_id}`;
		  const message_type = data.msg_type; // 'REQ', 'REPLY', etc.
		  animateEdge(edge_id, message_type);
		});
	});


const configs = reactive(
  vNG.defineConfigs<Node, Edge>({
    node: {
      normal: {
        type: "circle",
        radius: node => node.size ?? 20,       // default radius if size not set
        color: node => node.color ?? "#3498db", // default color
      },
      hover: {
        radius: node => (node.size ?? 20) + 4,
        color: node => node.color ?? "#2980b9",
      },
      selectable: true,
      label: {
        visible: node => !!node.name,   // show if node.label exists
        text: node => node.name,
        fontSize: 14,
        fontColor: "#2c3e50",
        fontWeight: "bold",
      },
      focusring: {
        color: "orange",
        width: 4,
      },
    },
    edge: {
      normal: {
        width: edge => Math.min(Math.max(edge.width ?? 1, 1), 4), // clamp width 1-4
        color: edge => edge.color ?? "#95a5a6",
        dasharray: edge => (edge.dashed ? "4" : "0"),
      },
      hover: {
        width: edge => Math.min(Math.max(edge.width ?? 1, 1), 4) + 1,
        color: edge => edge.color ?? "#7f8c8d",
      },
      label: {
        visible: edge => !!edge.label,
        text: edge => edge.label ?? "",
        fontSize: 12,
        fontColor: "#34495e",
      },
    },
    layout: {
      improvedLayout: true, // enable automatic layout improvements
    },
    interaction: {
      zoomable: true,
      draggable: true,
      pan: true,
    },
  })
);
</script>

<template>
	<Legend />
  <v-network-graph
    class="graph"
    :nodes="network.nodes"
    :edges="network.edges"
		:configs="configs"
  />
</template>

<style>
.graph {
	margin: auto;
  width: 1600px;
  height: 900px;
  border: 1px solid #000;
}
</style>
