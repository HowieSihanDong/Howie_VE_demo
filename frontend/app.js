const { createApp, ref } = Vue

createApp({
    setup() {
        const userQuestion = ref('')
        const results = ref([])
        const generatedSql = ref('')
        const isLoading = ref(false)
        const errorMessage = ref('')
        const isCacheHit = ref(false)

        const doQuery = async () => {
            if (!userQuestion.value) return;
            
            console.log("🚀 [前端] 准备发起请求，输入内容:", userQuestion.value);
            isLoading.value = true;
            errorMessage.value = '';
            results.value = [];
            generatedSql.value = '';
            isCacheHit.value = false;

            try {
                // 后端 API 地址
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ prompt: userQuestion.value })
                });
                
                console.log("📡 [前端] 收到后端原始响应:", response.status);
                const data = await response.json();
                console.log("📦 [前端] 解析后的数据:", data);
                
                if (data.status === 'success') {
                    results.value = data.data;
                    generatedSql.value = data.sql;
                    isCacheHit.value = data.cache_hit;
                } else {
                    errorMessage.value = '查询出错了：' + data.message;
                    generatedSql.value = data.sql;
                }
            } catch (err) {
                errorMessage.value = '无法连接到后端服务器，请确保 main.py 已经运行！';
            } finally {
                isLoading.value = false;
            }
        }

        return {
            userQuestion,
            results,
            generatedSql,
            isLoading,
            errorMessage,
            isCacheHit,
            doQuery
        }
    }
}).mount('#app')
