import itertools
import psutil
import random
import string
import timeit
import subprocess
import logging
import multiprocessing as mp
import time

pass_len = 6
USER = "administrador"
allowed_chars = string.ascii_lowercase + string.digits
shuffled_chars = ''.join(random.sample(allowed_chars, len(allowed_chars)))
part_size = len(allowed_chars) // pass_len
result_found = None


def check_pass(guess):
    pwd = '1234'

    if len(guess) != len(pwd):
        return False

    for i in range(len(pwd)):
        if pwd[i] != guess[i]:
            return False

    return True


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def on_password_found(result):
    global result_found
    logging.info('Result found!')
    result_found = result


def do_job(user, first_bits, process):
    logging.info(
        f'Running brute-force process: #{process}. First bits are: {first_bits}.')
    time.sleep(2)
    for combination in itertools.product(first_bits, shuffled_chars, shuffled_chars, shuffled_chars, shuffled_chars, shuffled_chars):
        logging.debug(combination)
        guess = ''.join(combination)
        logging.info(f'Process "#{process}" - Current guess: {guess}')
        if check_password(user, guess):
            logging.info(
                f'Process "#{process}" found the password. Password is: {guess}')
            return guess


def check_password(user, guess):
    command = './login ' + user + ' ' + guess
    logging.debug(f'Running: "{command}"')

    p = subprocess.Popen(command, universal_newlines=True,
                         shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    retcode = p.wait()
    return retcode == 0


def random_str(size):
    return ''.join(random.choices(allowed_chars, k=size))


def crack_password(user, length):
    guess = random_str(length)
    counter = itertools.count()
    trials = 1

    while True:
        i = next(counter) % length

        for c in allowed_chars:
            alt = guess[:i] + c + guess[i + 1:]

            alt_time = timeit.repeat(stmt='check_password(user, x)',
                                     setup=f'user={user!r};x={alt!r}',
                                     globals=globals(),
                                     number=trials,
                                     repeat=10)

            guess_time = timeit.repeat(stmt='check_password(user, x)',
                                       setup=f'user={user!r};x={guess!r}',
                                       globals=globals(),
                                       number=trials,
                                       repeat=10)

            if check_password(user, alt):
                return alt

            if min(alt_time) > min(guess_time):
                guess = alt
                logging.debug(f'Current guess: "{guess}"')


def brute_force_password(user, length):
    logging.info(f'Startup complete. Running brute-force.')
    logging.info(f'Generating all possible password combinations.')
    combinations = itertools.product(allowed_chars, repeat=length)
    logging.info(f'All possible passwords were generated.')

    for combination in combinations:
        guess = ''.join(combination)

        if check_password(user, guess):
            return guess


def async_brute_force_password(user, length):
    global result_found
    pool = mp.Pool(processes=4)

    for i in list(range(length)):
        if i == length - 1:
            first_bit = shuffled_chars[part_size * i:]
        else:
            first_bit = shuffled_chars[part_size * i: part_size * (i+1)]

        pool.apply_async(do_job, args=(
            user, first_bit, i), callback=on_password_found)

    pool.close()

    while result_found is None:
        time.sleep(2)

    pool.terminate()

    return result_found


def print_info():
    logging.info("Starting...")
    logging.info(f'User: "{USER}" and pass length of "{pass_len}".')
    logging.info(f'Allowed chars: "{allowed_chars}".')
    logging.info(f'Part size: {part_size}')

    logging.info("===================== CPU Info =====================")

    # Number of cores
    logging.info(f'Physical cores: {psutil.cpu_count(logical=False)}')
    logging.info(f'Total cores: {psutil.cpu_count(logical=True)}')

    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    logging.info(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    logging.info(f"Min Frequency: {cpufreq.min:.2f}Mhz")
    logging.info(f"Current Frequency: {cpufreq.current:.2f}Mhz")

    # Memory Information
    logging.info(
        "===================== Memory Information =====================")

    # Get the memory details
    svmem = psutil.virtual_memory()
    logging.info(f"Total: {get_size(svmem.total)}")
    logging.info(f"Available: {get_size(svmem.available)}")
    logging.info(f"Used: {get_size(svmem.used)}")
    logging.info(f"Percentage: {svmem.percent}%")

    logging.info("===================== SWAP =====================")

    # Get the swap memory details (if exists)
    swap = psutil.swap_memory()
    logging.info(f"Total: {get_size(swap.total)}")
    logging.info(f"Free: {get_size(swap.free)}")
    logging.info(f"Used: {get_size(swap.used)}")
    logging.info(f"Percentage: {swap.percent}%")

    logging.info("===================== DONE =====================")


def main():
    logging.basicConfig(filename='password-crack2.log', encoding='utf-8', level=logging.INFO,
                        format='%(asctime)s :: %(levelname)s :: %(message)s')
    print_info()
    # password = crack_password(user, pass_len)
    # password = brute_force_password(user, pass_len)
    password = async_brute_force_password(USER, pass_len)

    logging.info(f"Password cracked: '{password}'")
    logging.info("Done!")


if __name__ == '__main__':
    main()