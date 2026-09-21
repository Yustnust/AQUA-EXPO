# -*- coding: utf-8 -*-
# 在脚本库中同步插入 Param_Delay_ValveC_Verify(排液完成验证延时) 处理
p = 'archive/mcgspro/McgsPro脚本代码_54个_v2.0.md'
text = open(p, 'rb').read().decode('utf-8')
C = '\r\n'
reps = []

# A. 8个单元读取段: 活动值VD60 → Param缓冲区
for n in range(1, 9):
    reps.append((
        '    Param_Delay_ValveA_Verify = U%d_VD_Delay_ValveA_Verify' % n + C,
        '    Param_Delay_ValveA_Verify = U%d_VD_Delay_ValveA_Verify' % n + C
        + '    Param_Delay_ValveC_Verify = U%d_VD_Delay_ValveC_Verify' % n + C))

errA = ('IF  Param_Delay_ValveA_Verify < 0  THEN' + C
        + '    Param_Confirm_Text = "错误：阀A关闭延时验证设定值不能为负数"' + C
        + '    Param_Pending_Save = 0' + C
        + '    !OpenSubWnd(用户窗口.参数设置二次确认, 400, 300, 400, 200, 0)' + C
        + '    EXIT' + C + 'ENDIF' + C)
errC = ('IF  Param_Delay_ValveC_Verify < 0  THEN' + C
        + '    Param_Confirm_Text = "错误：排液完成验证延时设定值不能为负数"' + C
        + '    Param_Pending_Save = 0' + C
        + '    !OpenSubWnd(用户窗口.参数设置二次确认, 400, 300, 400, 200, 0)' + C
        + '    EXIT' + C + 'ENDIF' + C)
# B1. 保存参数校验(参数设置二次确认)
reps.append((errA, errA + errC))

errBA = ('IF  Param_Delay_ValveA_Verify < 0  THEN' + C
         + '    Param_Confirm_Text = "错误：进水阀关闭延时验证设定值不能为负数"' + C
         + '    Param_Pending_Save = 0' + C
         + '    !OpenSubWnd(用户窗口.保存默认二次确认, 400, 300, 400, 200, 0)' + C
         + '    EXIT' + C + 'ENDIF' + C)
errBC = ('IF  Param_Delay_ValveC_Verify < 0  THEN' + C
         + '    Param_Confirm_Text = "错误：排液完成验证延时设定值不能为负数"' + C
         + '    Param_Pending_Save = 0' + C
         + '    !OpenSubWnd(用户窗口.保存默认二次确认, 400, 300, 400, 200, 0)' + C
         + '    EXIT' + C + 'ENDIF' + C)
# B2. 保存默认校验(保存默认二次确认)
reps.append((errBA, errBA + errBC))

chkA = ('If Param_Delay_ValveA_Verify < 0 Then' + C
        + '    ParamValid = 0' + C
        + '    ParamInvalidStr = "阀A关闭延时验证设定值不能为负数"' + C
        + 'EndIf' + C)
chkC = ('If Param_Delay_ValveC_Verify < 0 Then' + C
        + '    ParamValid = 0' + C
        + '    ParamInvalidStr = "排液完成验证延时设定值不能为负数"' + C
        + 'EndIf' + C)
# B3. 复制到其他单元统一校验
reps.append((chkA, chkA + chkC))

# C. 脚本30 读取默认: UD(VD492) → Param
reps.append((
    'Param_Delay_ValveA_Verify = U1_UD_VD66_DelayA' + C,
    'Param_Delay_ValveA_Verify = U1_UD_VD66_DelayA' + C
    + 'Param_Delay_ValveC_Verify = U1_UD_VD60_DelayC' + C))

# D. 保存默认确认: Param → UD(VD492)
reps.append((
    '    U1_UD_VD66_DelayA        = Param_Delay_ValveA_Verify' + C,
    '    U1_UD_VD66_DelayA        = Param_Delay_ValveA_Verify' + C
    + '    U1_UD_VD60_DelayC        = Param_Delay_ValveC_Verify' + C))

# E. 参数设置确认: Param → 活动VD60
reps.append((
    '    U1_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify' + C,
    '    U1_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify' + C
    + '    U1_VD_Delay_ValveC_Verify = Param_Delay_ValveC_Verify' + C))

# F. 恢复出厂: 活动VD与Param缓冲区默认值
reps.append((
    '    U1_VD_Delay_ValveA_Verify= 5.0' + C,
    '    U1_VD_Delay_ValveA_Verify= 5.0' + C
    + '    U1_VD_Delay_ValveC_Verify= 5.0' + C))
reps.append((
    '    Param_Delay_ValveA_Verify = 5.0' + C,
    '    Param_Delay_ValveA_Verify = 5.0' + C
    + '    Param_Delay_ValveC_Verify = 5.0' + C))

ok = True
for i, (old, new) in enumerate(reps):
    cnt = text.count(old)
    if cnt != 1:
        print('#%d 匹配数=%d !!' % (i, cnt))
        ok = False
if ok:
    for old, new in reps:
        text = text.replace(old, new)
    open(p, 'wb').write(text.encode('utf-8'))
    print('全部 %d 处替换成功' % len(reps))
