from alicat import FlowController
import asyncio

class Test_works:
    def __init__(self, depo_flow_controller_com_port):
        self.depo_flow_controller_com_port = depo_flow_controller_com_port

    async def CO2purge(self):
        flow_controller = FlowController(f'{self.depo_flow_controller_com_port}')
        
        # Assuming that your get(), set_gas(), and set_flow_rate() methods are synchronous
        #print(await flow_controller.get())
        await flow_controller.set_gas('CO2')
        await asyncio.sleep(5)  # Pause for 10 seconds
        await flow_controller.set_gas('N2')
        await flow_controller.close()

    def auto_purge(self):
        asyncio.run(self.CO2purge())