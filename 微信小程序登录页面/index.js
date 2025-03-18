Page({
  data: {
    isLoading: false,
    isLoggedIn: false,
    userInfo: null
  },
  
  onLoad() {
    // 检查是否已登录
    this.checkLoginStatus();
  },
  
  onShow() {
    // 每次页面显示时检查登录状态
    this.checkLoginStatus();
  },
  
  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    
    if (token && userInfo) {
      this.setData({
        isLoggedIn: true,
        userInfo: userInfo
      });
    } else {
      this.setData({
        isLoggedIn: false,
        userInfo: null
      });
    }
  },
  
  // 用户点击登录按钮
  login() {
    this.setData({
      isLoading: true
    });
    
    // 获取用户信息
    wx.getUserProfile({
      desc: '用于完善会员资料',
      success: (userInfoRes) => {
        // 获取用户信息成功后，调用微信登录
        this.wxLogin(userInfoRes.userInfo);
      },
      fail: (err) => {
        this.setData({
          isLoading: false
        });
        
        if (err.errMsg.indexOf('cancel') > -1) {
          wx.showToast({
            title: '您已取消登录',
            icon: 'none'
          });
        } else {
          wx.showToast({
            title: '获取用户信息失败',
            icon: 'none'
          });
          console.error('获取用户信息失败', err);
        }
      }
    });
  },
  
  // 调用微信登录接口
  wxLogin(userInfo) {
    wx.login({
      success: (loginRes) => {
        if (loginRes.code) {
          // 将code和用户信息发送到后端
          this.sendLoginRequest(loginRes.code, userInfo);
        } else {
          this.handleLoginFail('登录失败');
          console.error('wx.login 失败', loginRes);
        }
      },
      fail: (err) => {
        this.handleLoginFail('网络异常');
        console.error('wx.login 网络异常', err);
      }
    });
  },
  
  // 发送登录请求到后端
  sendLoginRequest(code, userInfo) {
    wx.request({
      url: '域名/wx/login',
      method: 'POST',
      data: {
        code: code,
        user_info: userInfo
      },
      success: (res) => {
        this.setData({
          isLoading: false
        });
        
        if (res.statusCode === 200 && res.data.access_token) {
          // 保存登录状态和token
          wx.setStorageSync('token', res.data.access_token);
          wx.setStorageSync('userInfo', userInfo);
          wx.setStorageSync('loginTime', new Date().getTime());
          
          // 更新页面状态
          this.setData({
            isLoggedIn: true,
            userInfo: userInfo
          });
          
          wx.showToast({
            title: '登录成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: res.data.detail || '登录失败',
            icon: 'none'
          });
          console.error('登录失败', res);
        }
      },
      fail: (err) => {
        this.handleLoginFail('服务器连接失败');
        console.error('请求失败', err);
      }
    });
  },
  
  // 处理登录失败
  handleLoginFail(message) {
    this.setData({
      isLoading: false
    });
    
    wx.showToast({
      title: message,
      icon: 'none'
    });
  },
  
  // 跳转到文件上传页面
  goToFileUpload() {
    wx.navigateTo({
      url: '/pages/file_upload/file_upload'
    });
  },
  
  // 退出登录
  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除登录信息
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          wx.removeStorageSync('loginTime');
          
          // 更新页面状态
          this.setData({
            isLoggedIn: false,
            userInfo: null
          });
          
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          });
        }
      }
    });
  },
  
  // 显示隐私政策
  showPrivacyPolicy() {
    wx.navigateTo({
      url: '/pages/privacy/privacy'
    });
  }
});