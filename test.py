from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient("127.0.0.1", "502")
client.connect()
if client.connect():
    print("Modbus RTU Client Connected")
else:
    print("Failed to connect to Modbus RTU Client")
client.write_register(6,4, slave=1)
result = client.read_holding_registers(1, 5, slave=1)
print(result.registers)
client.close()
