import argparse

def log_filtering(input_file, filter_list, output_file=None, print_to_console=False):

    try:
        log_entries = extract_log_entries(input_file)
        filtered_entries = []

        for entry in log_entries:
            for f in filter_list:
                if f in entry:
                    filtered_entries.append(entry)

        print_output(filtered_entries, output_file, print_to_console)

        return filtered_entries

    except Exception as error:
        print("Caught error:" + str(error))

def print_output(entries, output_file, print_to_console):

    if not print_to_console and output_file is None:
        return

    result = ''.join(entries)

    if print_to_console:
        print(result)

    if output_file is not None:
        with open(output_file, 'w') as output_data:
            output_data.write(result)


def extract_log_entries(input_file):
    entries = []
    currentEntry = ''
    with open(input_file) as input_data:
        for line in input_data:
            if line[0:4] == '2018':
                #It is a new entry
                entries.append(currentEntry)
                currentEntry = line
            else:
                #Continuation of an entry
                currentEntry += line

    return entries[1:]

def get_omci_messages_exchanged(input_file, output_file, print_to_console):
    omci_logs = log_filtering(input_file, ['proxied_message'])
    omcis = []

    for log_entry in omci_logs:
        line = ''
        omci_message = log_entry.split('msg: ')[1].split(',')[0]
        onu_id = log_entry.split('onu_id: ')[1].split('\n')[0]
        if 'olt.send' in log_entry:
            line += 'OLT to ONU message, '
        else:
            line += 'ONU to OLT message, '
        line += 'onu_id {} : {}\n'.format(onu_id, omci_message)
        omcis.append(line)

    print_output(omcis, output_file, print_to_console)




parser = argparse.ArgumentParser(description='Voltha log filtering')
parser.add_argument("-f", "--inputFile", help = "log file to filter")
parser.add_argument("-o", "--outputFile", help = "filtered output file")
parser.add_argument("-d", "--debug", action='store_true', help = "filter on debug")
parser.add_argument("-i", "--info", action='store_true', help = "filter on info")
parser.add_argument("-w", "--warning", action='store_true', help = "filter on warning")
parser.add_argument("-e", "--error", action='store_true', help = "filter on error")
parser.add_argument("--omci", action='store_true', help = "filter the omci messages")

# TODO: force to have outputFile if noPrint
parser.add_argument("--noPrint", action='store_true', help = "does not print output")
parser.add_argument("filters", help="filters", nargs='*')

if __name__ == "__main__":

    args = parser.parse_args()

    if args.omci:
        get_omci_messages_exchanged(args.inputFile, args.outputFile, not args.noPrint)
    else:

        filter_list = []

        filter_list += args.filters

        if args.debug:
            filter_list.append('DEBUG')
        if args.info:
            filter_list.append('INFO')
        if args.warning:
            filter_list.append('WARNING')
        if args.error:
            filter_list.append('ERROR')
            filter_list.append('Error')

        log_filtering(args.inputFile, filter_list, args.outputFile, not args.noPrint)