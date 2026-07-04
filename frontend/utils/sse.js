/**
 * 微信小程序 SSE (Server-Sent Events) 客户端
 * 解决痛点：原生 wx.request 不支持 SSE、ArrayBuffer 中文乱码、数据粘包/半包
 */
class SSEClient {
  constructor(url, options) {
    this.url = url;
    this.options = options || {};
    this.buffer = ''; // 缓冲区，用于处理粘包/半包
    this.requestTask = null;
    
    // 初始化 UTF-8 解码器 (解决中文乱码)
    if (typeof TextDecoder !== 'undefined') {
      this.decoder = new TextDecoder('utf-8');
    }
  }

  connect(data) {
    this.requestTask = wx.request({
      url: this.url,
      method: 'POST',
      data: data,
      timeout: 300000, // 🌟 新增：将超时时间设置为 5 分钟 (300,000 毫秒)
      enableChunked: true, // 🌟 核心：开启分块传输 (基础库 2.20.2+)
      header: { 'Content-Type': 'application/json' },
      success: () => this.options.onClose && this.options.onClose(),
      fail: (err) => this.options.onError && this.options.onError(err)
    });

    // 监听分块数据
    this.requestTask.onChunkReceived((res) => {
      // res.data 是 ArrayBuffer 类型，需要解码为 String
      const text = this.decodeArrayBuffer(res.data);
      this.buffer += text;
      
      // 🌟 核心：处理粘包/半包
      // SSE 标准是以双换行符 \n\n 分隔事件
      const parts = this.buffer.split('\n\n');
      // 最后一个元素可能是不完整的数据，留在 buffer 里等下一个 chunk 拼接
      this.buffer = parts.pop(); 
      
      // 处理完整的 SSE 事件
      parts.forEach(part => {
        if (part.startsWith('data: ')) {
          const jsonStr = part.replace('data: ', '');
          try {
            const parsedData = JSON.parse(jsonStr);
            this.options.onMessage && this.options.onMessage(parsedData);
          } catch (e) {
            console.warn('SSE JSON 解析失败:', jsonStr);
          }
        }
      });
    });
  }

  // 将 ArrayBuffer 解码为 UTF-8 字符串
  decodeArrayBuffer(buffer) {
    if (this.decoder) {
      return this.decoder.decode(new Uint8Array(buffer));
    }
    // 兜底方案 (老旧基础库)
    const uint8Array = new Uint8Array(buffer);
    let text = '';
    for (let i = 0; i < uint8Array.length; i++) {
      text += String.fromCharCode(uint8Array[i]);
    }
    return decodeURIComponent(escape(text)); 
  }
  
  // 停止生成 (中断请求)
  close() {
    if (this.requestTask) {
      this.requestTask.abort();
      this.requestTask = null;
    }
  }
}

module.exports = SSEClient;
