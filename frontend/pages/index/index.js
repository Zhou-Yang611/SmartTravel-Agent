const SSEClient = require('../../utils/sse');

// 🌟 增强版：Markdown 转 HTML (适配小程序 rich-text 组件)
function markdownToHtml(md) {
  if (!md) return '';
  let html = md;
  
  // 处理标题 (注意顺序，先处理 ### 再处理 ## 再处理 #)
  html = html.replace(/^### (.*?)(\n|$)/gm, '<h3 style="font-size:16px;color:#333;margin:15px 0 8px;font-weight:bold;">$1</h3>');
  html = html.replace(/^## (.*?)(\n|$)/gm, '<h2 style="font-size:18px;color:#07c160;margin:20px 0 10px;border-bottom:1px solid #eee;padding-bottom:5px;font-weight:bold;">$1</h2>');
  html = html.replace(/^# (.*?)(\n|$)/gm, '<h1 style="font-size:22px;margin:20px 0;font-weight:bold;">$1</h1>');
  
  // 处理加粗
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color:#d4380d;">$1</strong>');
  
  // 处理无序列表 (简单的 - 或 * 开头)
  html = html.replace(/^[\-\*] (.*?)(\n|$)/gm, '<div style="padding-left:15px;position:relative;margin:5px 0;"><span style="position:absolute;left:0;">•</span> $1</div>');
  
  // 处理换行 (将连续的换行合并，单个换行转为 <br>)
  html = html.replace(/\n\n/g, '<div style="height:10px;"></div>');
  html = html.replace(/\n/g, '<br/>');
  
  return html;
}

Page({
  data: {
    userInput: '',
    isLoading: false,
    statusText: '',
    formattedItinerary: ''
  },

  sseClient: null,

  onInput(e) {
    this.setData({ userInput: e.detail.value });
  },

  onSend() {
    if (!this.data.userInput.trim()) return;

    this.setData({ 
      isLoading: true, 
      formattedItinerary: '', 
      statusText: '🚀 正在唤醒 Multi-Agent 团队...' 
    });

    // 🌟 注意：这里的 IP 地址！
    // 如果后端和开发者工具在同一台电脑，使用 127.0.0.1
    // 如果用真机调试，必须填你电脑的局域网 IP (如192.168.10.8 )
    const backendUrl = 'http://192.168.10.8:8000/api/chat/stream';

    this.sseClient = new SSEClient(backendUrl, {
      onMessage: (data) => this.handleSSEMessage(data),
      onError: (err) => {
        console.error('SSE Error:', err);
        this.setData({ isLoading: false, statusText: '❌ 连接后端失败，请检查网络或后端服务是否启动。' });
      },
      onClose: () => {
        console.log('SSE 连接正常关闭');
        this.setData({ isLoading: false });
      }
    });

    this.sseClient.connect({ 
      user_input: this.data.userInput,
      session_id: `wx_${Date.now()}` 
    });
  },

  onStop() {
    if (this.sseClient) {
      this.sseClient.close();
      this.setData({ isLoading: false, statusText: '⏹️ 已停止生成' });
    }
  },

  handleSSEMessage(data) {
    const { type, content } = data;
    
    if (type === 'status' || type === 'review') {
      this.setData({ statusText: content });
    } 
    else if (type === 'itinerary_chunk') {
      // 拼接流式文本并实时转换渲染
      const currentMd = this.data.currentMd || '';
      const newMd = currentMd + content;
      this.setData({ 
        currentMd: newMd,
        formattedItinerary: markdownToHtml(newMd)
      });
    } 
    else if (type === 'done') {
      this.setData({ statusText: '✅ ' + content, isLoading: false });
    }
    else if (type === 'error') {
      this.setData({ statusText: '❌ ' + content, isLoading: false });
    }
  },

  onUnload() {
    if (this.sseClient) this.sseClient.close();
  }
});
