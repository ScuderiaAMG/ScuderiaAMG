from scipy.io import loadmat
  mat = loadmat('D:\\Repositories\\ScuderiaAMG\\PINN_CNN\\data\\nasa_pcoe\\B0005.mat')
  b = mat['B0005'][0,0]
  # 看第一个 charge cycle 的 data 结构
  for i in range(len(b['cycle'][0])):
      t = b['cycle'][0,i]['type'][0]
      if hasattr(t, 'decode'): t = t.decode()
      if str(t).strip().lower() == 'charge':
          d = b['cycle'][0,i]['data'][0,0]
          print('Fields:', list(d.dtype.names))
          print('Voltage shape:', d['Voltage_measured'][0,0].shape)
          print('Current shape:', d['Current_measured'][0,0].shape)
          print('Temp shape:', d['Temperature_measured'][0,0].shape)
          print('Time shape:', d['Time'][0,0].shape)
          break