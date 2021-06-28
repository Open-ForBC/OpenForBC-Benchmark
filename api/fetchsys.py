from GPUtil import getGPUs
import psutil as psu


class SystemDescription:
    def get_gpu_info(self, gpuid=0) -> dict():
        gtype = getGPUs()
        gpu_info = {
            "GPUName": gtype[gpuid].name,
            "uuid": gtype[gpuid].uuid,
            "memoryTotal": str(gtype[gpuid].memoryTotal) + " MB",
            "memoryUsed": str(gtype[gpuid].memoryUsed) + " MB",
            "driverVersion": gtype[gpuid].driver,
        }
        return gpu_info

    def get_system_info(self) -> dict():
        with open("/proc/cpuinfo", "r") as f:
            info = f.readlines()
        cpuinfo = [x.strip().split(":")[1] for x in info if "model name" in x][0]
        mem = psu.virtual_memory()
        system_info = {
            "cpuInfo": str(cpuinfo),
            "totalMemory": str(round(mem.total / 1e6)) + " MB",
            "availableMemory": str(round(mem.available / 1e6)) + " MB",
            "usedMemory": str(round(mem.used / 1e6)) + " MB",
            "percentUsed": round((mem.used / mem.total) * 100),
        }
        return system_info


def main():
    inst = SystemDescription()
    print(inst.get_system_info())


if __name__ == "__main__":
    main()
