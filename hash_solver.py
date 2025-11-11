from Pyro4 import expose
import hashlib 

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Inited")
        
    def solve(self):
        print("Job Started")
        
        try:
            target_hash, salt, pin_length = self.read_input()
        except Exception as e:
            print("Error: Could not read input file.")
            self.write_output(None, target_hash, salt)
            return
            
        print("Workers: %d" % len(self.workers))

        CHARSET = 'abcdefghijklmnopqrstuvwxyz0123456789'
        BASE = len(CHARSET)
        
        total_space = BASE**pin_length
        print("Total combinations to check: %d" % total_space)
        
        chunk_size = total_space // len(self.workers)
        
        mapped = []
        for i in range(len(self.workers)):
            range_start = i * chunk_size
            range_end = (i + 1) * chunk_size if i < len(self.workers) - 1 else total_space
            
            print("Worker %d: checking range [%d, %d)" % (i, range_start, range_end))
            
            mapped.append(self.workers[i].mymap(
                str(range_start), 
                str(range_end), 
                target_hash, 
                str(pin_length),
                salt,
                CHARSET
            ))

        result_list = self.myreduce(mapped)
        found_pin = None
        if result_list:
            found_pin = result_list[0]

        self.write_output(found_pin, target_hash, salt)
        print("Job Finished")

    @staticmethod
    @expose
    def mymap(range_start_str, range_end_str, target_hash, pin_length_str, salt, charset):
        
        range_start = int(range_start_str)
        range_end = int(range_end_str)
        pin_length = int(pin_length_str)
        
        found = []

        for num in xrange(range_start, range_end):
            pin = Solver.int_to_base_str(num, charset, pin_length)
            
            if Solver.check_hash(pin, salt, target_hash):
                print("FOUND: %s" % pin)
                found.append(pin)  

        return found

    @staticmethod
    @expose
    def int_to_base_str(n, charset, min_length):
        base = len(charset)
        if n == 0:
            res = charset[0]
        else:
            res = ""
            while n > 0:
                n, rem = divmod(n, base)
                res = charset[rem] + res
        
        current_len = len(res)
        if current_len < min_length:
            padding = ""
            for i in xrange(min_length - current_len):
                padding += charset[0]
            return padding + res
        else:
            return res

    @staticmethod
    @expose
    def check_hash(pin, salt, target_hash):
        salted_pin = pin + salt
        attempt_hash = hashlib.md5(salted_pin).hexdigest()
        return attempt_hash == target_hash

    @staticmethod
    @expose
    def myreduce(mapped):
        print("Reduce started")
        result = []
        for worker_result in mapped:
            if worker_result.value: 
                result.extend(worker_result.value)
        print("Reduce finished")
        return result

    def read_input(self):
        f = open(self.input_file_name, 'r')
        target_hash = f.readline().strip()
        salt = f.readline().strip()
        pin_length = int(f.readline().strip())
        f.close()
        return target_hash, salt, pin_length

    def write_output(self, found_pin, target_hash, salt):
        with open(self.output_file_name, 'w') as f:
            if found_pin:
                f.write("Original PIN: %s\n" % found_pin)
                f.write("Target Hash: %s\n" % target_hash)
                f.write("Salt: %s\n" % salt)
            else:
                f.write("PIN not found\n")
                f.write("Target Hash: %s\n" % target_hash)
                f.write("Salt: %s\n" % salt)
        print("Output written.")