import requests
import FyresIntegration
import time
from datetime import datetime, timedelta
import pandas as pd
import os
import sys
import traceback


from datetime import datetime

def weekly_exp_contract_date(date_str, ex, ex_underlying_symbol, strike, opt_type):
    parsed_date = datetime.strptime(date_str, "%d-%b-%y")
    year = parsed_date.strftime("%y")  # Two-digit year
    month = parsed_date.strftime("%m").lstrip("0")  # Remove leading zero from month
    day = parsed_date.strftime("%d")  # Two-digit day
    formatted_date = f"{year}{month}{day}"
    final_symbol = f"{ex}:{ex_underlying_symbol}{formatted_date}{strike}{opt_type}"
    return final_symbol

# Example usage




def monthly_exp_contract_date(date_str, ex, ex_underlying_symbol, strike,opt_type):

    parsed_date = datetime.strptime(date_str, "%d-%b-%y")

    # Format the date to {YY}{MMM} (e.g., "24NOV")
    formatted_date = parsed_date.strftime("%y%b").upper()

    # Construct the final symbol
    final_symbol = f"{ex}:{ex_underlying_symbol}{formatted_date}{strike}{opt_type}"

    return final_symbol


def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')

def round_to_nearest(number, nearest):
    return round(number / nearest) * nearest



def get_user_settings():
    delete_file_contents("OrderLog.txt")
    global result_dict
    # Symbol,lotsize,Stoploss,Target1,Target2,Target3,Target4,Target1Lotsize,Target2Lotsize,Target3Lotsize,Target4Lotsize,BreakEven,ReEntry
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}
        # Symbol,EMA1,EMA2,EMA3,EMA4,lotsize,Stoploss,Target,Tsl
        for index, row in df.iterrows():
            # TYPE	EXPIRY	STRIKE_LOWEST	STRIKE_HIGHEST	START TIME	STOP TIME	ContractType	ProductType	STRIKE STEP	STRATEGYTAG Mode	TradeExp
            symbol_dict = {
                'SYMBOL': row['SYMBOL'],'BaseSymBol':row['BaseSymBol'],"Quantity":row['Quantity'],'TYPE':row['TYPE'],
                'EXPIRY':row['EXPIRY'],'STRIKE_LOWEST':row['STRIKE_LOWEST'],'STRIKE_HIGHEST':row['STRIKE_HIGHEST'],
                'START TIME':row['START TIME'],'STOP TIME':row['STOP TIME'],'ProductType':row['ProductType'],'ContractType':row['ContractType'],
                'STRIKE STEP':row['STRIKE STEP'],'STRATEGYTAG':row['STRATEGYTAG'],'Mode':row['Mode'],'TradeExp':row['TradeExp'],
                'InitialAtm': None,'UpLevel': None,'Downlevel': None,'InitialLevelRun':None,'ltp':None,'PrevLevel':None,'First':None,
                'callstrike':None,'putstrike':None,'trade_exp':None,'CycleCount':row['CycleCount'],'TradeCount':0,'TimeBasedExit':None,
                'LmtPercentage':row['LmtPercentage'],
            }
            result_dict[row['SYMBOL']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

def get_api_credentials():
    credentials = {}

    try:
        df = pd.read_csv('Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials
import requests
import pandas as pd

def download_symbols(url, filename):
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame.from_dict(data, orient='index')
    column_mapping = {
        "lastUpdate": "lastUpdate", "exSymbol": "exSymbol", "qtyMultiplier": "qtyMultiplier",
        "previousClose": "previousClose", "exchange": "exchange", "exSeries": "exSeries",
        "optType": "optType", "mtf_margin": "mtf_margin", "is_mtf_tradable": "is_mtf_tradable",
        "exSymName": "exSymName", "symTicker": "symTicker", "exInstType": "exInstType",
        "fyToken": "fyToken", "upperPrice": "upperPrice", "lowerPrice": "lowerPrice",
        "segment": "segment", "symbolDesc": "symbolDesc", "symDetails": "symDetails",
        "exToken": "exToken", "strikePrice": "strikePrice", "minLotSize": "minLotSize",
        "underFyTok": "underFyTok", "currencyCode": "currencyCode", "underSym": "underSym",
        "expiryDate": "expiryDate", "tradingSession": "tradingSession", "asmGsmVal": "asmGsmVal",
        "faceValue": "faceValue", "tickSize": "tickSize", "exchangeName": "exchangeName",
        "originalExpDate": "originalExpDate", "isin": "isin", "tradeStatus": "tradeStatus",
        "qtyFreeze": "qtyFreeze", "previousOi": "previousOi", "fetchHistory": None
    }
    df.rename(columns=column_mapping, inplace=True)
    for col in column_mapping.values():
        if col not in df.columns:
            df[col] = None
    df.to_csv(filename, index=False)
    print(f'Data successfully written to {filename}')

# Define the URLs and corresponding filenames
links = {
    "NSE_FO": "https://public.fyers.in/sym_details/NSE_FO_sym_master.json",
    "NSE_CM": "https://public.fyers.in/sym_details/NSE_CM_sym_master.json",
    "MCX_COM": "https://public.fyers.in/sym_details/MCX_COM_sym_master.json"
}

# for name, url in links.items():
#     filename = f"{name}_Instrument.csv"
#     download_symbols(url, filename)



get_user_settings()
credentials_dict = get_api_credentials()
redirect_uri = credentials_dict.get('redirect_uri')
client_id = credentials_dict.get('client_id')
secret_key = credentials_dict.get('secret_key')
grant_type = credentials_dict.get('grant_type')
response_type = credentials_dict.get('response_type')
state = credentials_dict.get('state')
TOTP_KEY = credentials_dict.get('totpkey')
FY_ID = credentials_dict.get('FY_ID')
PIN = credentials_dict.get('PIN')

FyresIntegration.automated_login(client_id=client_id, redirect_uri=redirect_uri, secret_key=secret_key, FY_ID=FY_ID,
                                     PIN=PIN, TOTP_KEY=TOTP_KEY)


def create_websocket():
    # MCX:CRUDEOIL20OCTFUT,NSE:NIFTY20OCTFUT,
    global result_dict
    symbol_list = []
    for key, value in result_dict.items():
        if 'SYMBOL' in value and 'Mode' in value:
            symbol = value['SYMBOL']

            if value['Mode'] == 'FUTURE' and 'EXPIRY' in value:
                expiry_date = value['EXPIRY']
                expiry_key_date = datetime.strptime(expiry_date, "%d-%b-%y").strftime("%y%b").upper()
                formatted_symbol = f"NSE:{symbol}{expiry_key_date}FUT"
            elif value['Mode'] == 'SPOT':
                formatted_symbol = f"NSE:{symbol}"
            elif value['Mode'] == 'MCX':
                expiry_date = value['EXPIRY']
                expiry_key_date = datetime.strptime(expiry_date, "%d-%b-%y").strftime("%y%b").upper()
                formatted_symbol = f"MCX:{symbol}{expiry_key_date}FUT"
            else:
                continue  # Skip if 'Mode' is neither 'Future' nor 'SPOT'

            symbol_list.append(formatted_symbol)

    FyresIntegration.fyres_websocket(symbol_list)
    print("symbol_list:", symbol_list)
    print("Web Socket created...")

create_websocket()


def generate_ce_otm_strike_prices(lowest, highest, strike_step, ltp):
    base_strike = (ltp // strike_step) * strike_step
    strikes = [int(base_strike + (i * strike_step)) for i in range(lowest, highest + 1)]
    return strikes

def generate_pe_otm_strike_prices(lowest, highest, strike_step, ltp):
    base_strike = (ltp // strike_step) * strike_step
    strikes = [int(base_strike - (i * strike_step)) for i in range(lowest, highest + 1)]
    return strikes

def generate_symbols_string_ce(params, segment):
    symbols_string = ""  # Initialize an empty string to hold the symbols
    for strike in params['callstrike']:
        if params['ContractType'] == "MONTHLY":
            symbol = monthly_exp_contract_date(
                date_str=params['TradeExp'],
                ex=segment,
                ex_underlying_symbol=params['BaseSymBol'],
                strike=strike,
                opt_type="CE"
            )
        elif params['ContractType'] == "WEEKLY":
            symbol = weekly_exp_contract_date(
                date_str=params['TradeExp'],
                ex=segment,
                ex_underlying_symbol=params['BaseSymBol'],
                strike=strike,
                opt_type="CE"
            )
        else:
            continue  # Skip if ContractType is not recognized

        # Append the generated symbol to the string
        symbols_string += f"{symbol},"

    # Remove the trailing comma
    symbols_string = symbols_string.rstrip(",")

    return symbols_string

def generate_symbols_string_pe(params, segment):
    symbols_string = ""  # Initialize an empty string to hold the symbols
    for strike in params['putstrike']:
        if params['ContractType'] == "MONTHLY":
            symbol = monthly_exp_contract_date(
                date_str=params['TradeExp'],
                ex=segment,
                ex_underlying_symbol=params['BaseSymBol'],
                strike=strike,
                opt_type="PE"
            )
        elif params['ContractType'] == "WEEKLY":
            symbol = weekly_exp_contract_date(
                date_str=params['TradeExp'],
                ex=segment,
                ex_underlying_symbol=params['BaseSymBol'],
                strike=strike,
                opt_type="PE"
            )
        else:
            continue  # Skip if ContractType is not recognized

        # Append the generated symbol to the string
        symbols_string += f"{symbol},"

    # Remove the trailing comma
    symbols_string = symbols_string.rstrip(",")

    return symbols_string

def calculate_percentage(number, percentage):
    return (number * percentage) / 100

def main_strategy():
    print("main_strategy running ")
    Algofoxid = credentials_dict.get('Algofoxid')
    Algofoxpassword = credentials_dict.get('Algofoxpassword')
    role = credentials_dict.get('role')
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['SYMBOL']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                EntryTime = params['START TIME']
                EntryTime = datetime.strptime(EntryTime, "%H:%M").time()
                ExitTime = params['STOP TIME']
                ExitTime = datetime.strptime(ExitTime, "%H:%M").time()
                current_time = datetime.now().time()
                symbol_value = params['SYMBOL']
                expiry_date = datetime.strptime(params['EXPIRY'], '%d-%b-%y').strftime("%y%b").upper()
                if params['Mode']=="FUTURE":
                    formatted_symbol = f"NSE:{symbol_value}{expiry_date}FUT"
                    segment="NSE"
                if params['Mode']=="MCX":
                    formatted_symbol = f"MCX:{symbol_value}{expiry_date}FUT"
                    segment = "MCX"
                if params['Mode']=="SPOT":
                    formatted_symbol = f"NSE:{symbol_value}"
                    segment = "NSE"
                ltp = FyresIntegration.shared_data.get(formatted_symbol)
                # 'CycleCount':row['CycleCount'],'TradeCount':0,
                if  current_time.strftime("%H:%M") >= EntryTime.strftime("%H:%M") and current_time.strftime("%H:%M") < ExitTime.strftime("%H:%M") :
                    if ltp is not None and params['InitialLevelRun']is None:
                        params['ltp']=ltp
                        params['InitialAtm']=round_to_nearest(params['ltp'],params['STRIKE STEP'])
                        if params['InitialAtm']> params['ltp'] :
                            params['UpLevel']=params['InitialAtm']+params['STRIKE STEP']
                            params['Downlevel'] = params['InitialAtm'] - params['STRIKE STEP']
                            Orderlog = f"{timestamp} Symbol : {params['SYMBOL']}, InitialAtm: {params['InitialAtm']}, Uplevel:{params['UpLevel']} ,Downlevel:{params['Downlevel']}"
                            print(Orderlog)
                            write_to_order_logs(Orderlog)

                        if params['InitialAtm'] < params['ltp'] :
                            params['UpLevel'] = params['InitialAtm'] + params['STRIKE STEP']
                            params['Downlevel'] = params['InitialAtm'] - params['STRIKE STEP']
                            Orderlog = f"{timestamp} Symbol : {params['SYMBOL']}, InitialAtm: {params['InitialAtm']}, Uplevel:{params['UpLevel']} ,Downlevel:{params['Downlevel']}"
                            print(Orderlog)
                            write_to_order_logs(Orderlog)

                        params['callstrike'] = generate_ce_otm_strike_prices(lowest=params['STRIKE_LOWEST'],
                                                                             highest=params['STRIKE_HIGHEST'],
                                                                             strike_step=params['STRIKE STEP'],
                                                                             ltp=params['ltp'])

                        params['putstrike'] = generate_pe_otm_strike_prices(lowest=params['STRIKE_LOWEST'],
                                                                            highest=params['STRIKE_HIGHEST'],
                                                                            strike_step=params['STRIKE STEP'],
                                                                            ltp=params['ltp'])
                        params['TimeBasedExit']= "TAKEEXIT"
                        if params['TYPE'] == 'SHORT':
                            trade_exp = datetime.strptime(params['TradeExp'], "%d-%b-%y").strftime("%d%b%Y").upper()
                            params['trade_exp']=trade_exp

                            symbols_string =generate_symbols_string_ce(params, segment=segment)
                            print("symbols_string: ",symbols_string)
                            quote_res = FyresIntegration.fyres_quote_ltp(symbols_string)
                            symbol_to_lp = {item['n']: item['v']['lp'] for item in quote_res['d']}
                            print("quote_res: ", quote_res)
                            for strike in params['callstrike']:
                                if params['ContractType']=="MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="CE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol =weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                     ex_underlying_symbol=params['BaseSymBol'],
                                                                     strike=strike,
                                                                     opt_type="CE")


                                print("symbol: ",symbol)
                                try:
                                    if params['LmtPercentage']==0:
                                        FyresIntegration.fyers_single_order(symbol=symbol,qty=params["Quantity"],
                                                                            side=-1,product=params['ProductType'],limit=0,type=2)

                                    if params['LmtPercentage'] > 0:
                                        # Extract 'lp' value for the symbol
                                        if symbol in symbol_to_lp:
                                            lp_value = symbol_to_lp[symbol]
                                            percentage_value=calculate_percentage(lp_value, params['LmtPercentage'])
                                            ep=lp_value-percentage_value
                                            ep = int(ep) + 0.05
                                            print(f"Using lp value for {symbol}: {ep}")

                                            FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                                side=-1, product=params['ProductType'],
                                                                                limit=ep, type=1)
                                except Exception as e:
                                    print("Error in main strategy : ", str(e))
                                    traceback.print_exc()





                                # Algofox.Short_order_algofox(symbol, quantity=params["Quantity"], instrumentType='OTPIDX',
                                #                             direction='BUY', product='MIS', strategy=params["STRATEGYTAG"],
                                #                             order_typ="MARKET", price=0, username=Algofoxid,
                                #                             password=Algofoxpassword, role=role,
                                #                             trigger=None, sll_price=None)
                            symbols_string = generate_symbols_string_pe(params, segment=segment)
                            print("symbols_string: ", symbols_string)
                            quote_res = FyresIntegration.fyres_quote_ltp(symbols_string)
                            symbol_to_lp = {item['n']: item['v']['lp'] for item in quote_res['d']}
                            print("symbol_to_lp: ", symbol_to_lp)
                            for strike in params['putstrike']:
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                   ex=segment,
                                                                   ex_underlying_symbol=params['BaseSymBol'],
                                                                   strike=strike, opt_type="PE")
                                if params['ContractType'] == "WEEKLY":
                                    symbol =weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                     ex_underlying_symbol=params['BaseSymBol'],
                                                                     strike=strike,
                                                                     opt_type="PE")


                                print("symbol: ", symbol)
                                try:
                                    if params['LmtPercentage'] == 0:
                                        FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                            side=-1, product=params['ProductType'],limit=0,type=2)
                                    if params['LmtPercentage'] > 0:
                                        # Extract 'lp' value for the symbol
                                        if symbol in symbol_to_lp:
                                            lp_value = symbol_to_lp[symbol]
                                            percentage_value=calculate_percentage(lp_value, params['LmtPercentage'])
                                            ep=lp_value-percentage_value
                                            ep = int(ep) + 0.05
                                            print(f"Using lp value for {symbol}: {ep}")
                                            FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                                side=-1, product=params['ProductType'],
                                                                                limit=ep, type=1)
                                except Exception as e:
                                    print("Error in main strategy : ", str(e))
                                    traceback.print_exc()

                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|PE"
                                # Algofox.Short_order_algofox(symbol, quantity=params["Quantity"], instrumentType='OTPIDX',
                                #                             direction='BUY', product='MIS', strategy=params["STRATEGYTAG"],
                                #                             order_typ="MARKET", price=0, username=Algofoxid,
                                #                             password=Algofoxpassword, role=role,
                                #                             trigger=None, sll_price=None)

                        if params['TYPE'] == 'BUY':
                            trade_exp = datetime.strptime(params['TradeExp'], "%d-%b-%y").strftime("%d%b%Y").upper()
                            params['trade_exp']=trade_exp

                            symbols_string = generate_symbols_string_ce(params, segment=segment)
                            print("symbols_string: ", symbols_string)
                            quote_res = FyresIntegration.fyres_quote_ltp(symbols_string)
                            symbol_to_lp = {item['n']: item['v']['lp'] for item in quote_res['d']}
                            print("symbol_to_lp: ", symbol_to_lp)
                            for strike in params['callstrike']:
                                if params['ContractType']=="MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="CE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol =weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                     ex_underlying_symbol=params['BaseSymBol'],
                                                                     strike=strike,
                                                                     opt_type="CE")

                                print("symbol: ", symbol)
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol,qty=params["Quantity"],
                                                                        side=1,product=params['ProductType'],type=2,limit=0)

                                if params['LmtPercentage'] > 0:
                                    # Extract 'lp' value for the symbol
                                    if symbol in symbol_to_lp:
                                        lp_value = symbol_to_lp[symbol]
                                        percentage_value=calculate_percentage(lp_value, params['LmtPercentage'])
                                        ep=lp_value+percentage_value
                                        ep = int(ep) + 0.05
                                        print(f"Using lp value for {symbol}: {ep}")
                                        FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                            side=1, product=params['ProductType'],
                                                                            limit=ep, type=1)


                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|CE"
                                # Algofox.Buy_order_algofox(symbol, quantity=params["Quantity"],
                                #                           instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                           strategy=params["STRATEGYTAG"],
                                #                           order_typ="MARKET", price=0, username=Algofoxid,
                                #                           password=Algofoxpassword, role=role,
                                #                           trigger=None, sll_price=None)
                            symbols_string = generate_symbols_string_pe(params, segment=segment)
                            print("symbols_string: ", symbols_string)
                            quote_res = FyresIntegration.fyres_quote_ltp(symbols_string)
                            symbol_to_lp = {item['n']: item['v']['lp'] for item in quote_res['d']}
                            print("symbol_to_lp: ", symbol_to_lp)
                            print("params['putstrike']: ",params['putstrike'])
                            for strike in params['putstrike']:
                                if params['ContractType']=="MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="PE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol =weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                     ex_underlying_symbol=params['BaseSymBol'],
                                                                     strike=strike,
                                                                     opt_type="PE")

                                print("symbol: ", symbol)
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol,qty=params["Quantity"],
                                                                        side=1,product=params['ProductType'],type=2,limit=0)
                                if params['LmtPercentage'] > 0:
                                    if symbol in symbol_to_lp:
                                        lp_value = symbol_to_lp[symbol]
                                        percentage_value = calculate_percentage(lp_value, params['LmtPercentage'])
                                        ep = lp_value + percentage_value
                                        ep = int(ep) + 0.05
                                        print(f"Using lp value for {symbol}: {lp_value}")
                                        FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                            side=1, product=params['ProductType'],
                                                                            limit=ep, type=1)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|PE"
                                # Algofox.Buy_order_algofox(symbol, quantity=params["Quantity"],
                                #                           instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                           strategy=params["STRATEGYTAG"],
                                #                           order_typ="MARKET", price=0, username=Algofoxid,
                                #                           password=Algofoxpassword, role=role,
                                #                           trigger=None, sll_price=None)

                        params['TradeCount']= params['TradeCount']+1

                        Orderlog = f"{timestamp} Initial trade {params['TYPE']} {params['SYMBOL']} for call in strike {params['callstrike']}"
                        print(Orderlog)
                        write_to_order_logs(Orderlog)
                        Orderlog = f"{timestamp} Initial trade {params['TYPE']} {params['SYMBOL']} for put in strike {params['putstrike']}"
                        print(Orderlog)
                        write_to_order_logs(Orderlog)

                        params['InitialLevelRun']="DONE"




                        print("callstrike: ",params['callstrike'])
                        print("putstrike: ", params['putstrike'])
                        if (
                                params['ltp']<=params['Downlevel'] and
                                params['Downlevel'] is not None and
                                params['InitialLevelRun'] =="DONE" and
                                params['TradeCount'] < params['CycleCount']
                        ):
                            # opening pos logic
                            params['UpLevel'] = params['Downlevel'] + params['STRIKE STEP']
                            params['Downlevel'] = params['Downlevel'] - params['STRIKE STEP']
                            params['PrevLevel'] = 'DownLevel'
                            params['TradeCount'] = params['TradeCount'] + 1
                            if params['TYPE'] == 'SHORT':
                                # exit pos logic

                                strike= max(params['callstrike'])
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="CE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=strike,
                                                                      opt_type="CE")

                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|CE"
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=1, product=params['ProductType'],type=2,limit=0)

                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp+percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)

                                # Algofox.Cover_order_algofox(symbol, quantity=params["Quantity"],
                                #                               instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                               strategy=params["STRATEGYTAG"],
                                #                               order_typ="MARKET", price=0, username=Algofoxid,
                                #                               password=Algofoxpassword, role=role,
                                #                               trigger=None, sll_price=None)


                                params['callstrike'].remove(strike)
                                Orderlog = f"{timestamp} Downside level @ {params['SYMBOL']} trade: {params['TYPE']} exit call strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)
                                # put
                                strike = max(params['putstrike'])
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="PE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=strike,
                                                                      opt_type="PE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=1, product=params['ProductType'],type=2,limit=0)

                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp+percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)

                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|PE"
                                # Algofox.Cover_order_algofox(symbol, quantity=params["Quantity"],
                                #                            instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                            strategy=params["STRATEGYTAG"],
                                #                            order_typ="MARKET", price=0, username=Algofoxid,
                                #                            password=Algofoxpassword, role=role,
                                #                            trigger=None, sll_price=None)

                                params['putstrike'].remove(strike)

                                Orderlog = f"{timestamp} Downside level @ {params['SYMBOL']} trade: {params['TYPE']} exit put strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)
                                # opening pos logic
                                lowest_strike = min(params['callstrike'])
                                new_strike = lowest_strike - params['STRIKE STEP']
                                params['callstrike'].append(new_strike)
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=new_strike, opt_type="CE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=new_strike,
                                                                      opt_type="CE")

                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=-1, product=params['ProductType'],type=2,limit=0)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp-percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)

                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{new_strike}|CE"
                                # Algofox.Short_order_algofox(symbol, quantity=params["Quantity"],
                                #                           instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                           strategy=params["STRATEGYTAG"],
                                #                           order_typ="MARKET", price=0, username=Algofoxid,
                                #                           password=Algofoxpassword, role=role,
                                #                           trigger=None, sll_price=None)
                                Orderlog = f"{timestamp} Downside level @ {params['SYMBOL']} trade: {params['TYPE']} entry call strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)

                                lowest_strike = min(params['putstrike'])
                                new_strike = int(lowest_strike - params['STRIKE STEP'])
                                params['putstrike'].append(new_strike)
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=new_strike, opt_type="PE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=new_strike,
                                                                      opt_type="PE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=-1, product=params['ProductType'],limit=0,type=2)

                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp-percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)

                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{new_strike}|PE"
                                # Algofox.Short_order_algofox(symbol, quantity=params["Quantity"],
                                #                           instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                           strategy=params["STRATEGYTAG"],
                                #                           order_typ="MARKET", price=0, username=Algofoxid,
                                #                           password=Algofoxpassword, role=role,
                                #                           trigger=None, sll_price=None)
                                Orderlog = f"{timestamp} Downside level @ {params['SYMBOL']} trade: {params['TYPE']} entry put strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)

                            if params['TYPE'] == 'BUY':
                                # exit pos logic
                                strike= max(params['callstrike'])
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="CE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=strike,
                                                                      opt_type="CE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=-1, product=params['ProductType'],limit=0,type=2)

                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp-percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)

                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|CE"
                                # Algofox.Sell_order_algofox(symbol, quantity=params["Quantity"],
                                #                               instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                               strategy=params["STRATEGYTAG"],
                                #                               order_typ="MARKET", price=0, username=Algofoxid,
                                #                               password=Algofoxpassword, role=role,
                                #                               trigger=None, sll_price=None)
                                params['callstrike'].remove(strike)
                                Orderlog = f"{timestamp} Downside level @ {params['SYMBOL']} trade: {params['TYPE']} exit call strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)

                                strike = max(params['putstrike'])
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="PE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=strike,
                                                                      opt_type="PE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=-1, product=params['ProductType'],limit=0,type=2)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp-percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|PE"
                                # Algofox.Sell_order_algofox(symbol, quantity=params["Quantity"],
                                #                            instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                            strategy=params["STRATEGYTAG"],
                                #                            order_typ="MARKET", price=0, username=Algofoxid,
                                #                            password=Algofoxpassword, role=role,
                                #                            trigger=None, sll_price=None)
                                params['putstrike'].remove(strike)
                                Orderlog = f"{timestamp} Downside level @ {params['SYMBOL']} trade: {params['TYPE']} exit put strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)
                                # opening pos logic
                                lowest_strike = min(params['callstrike'])
                                new_strike = lowest_strike - params['STRIKE STEP']
                                params['callstrike'].append(new_strike)
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=new_strike, opt_type="CE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=new_strike,
                                                                      opt_type="CE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=1, product=params['ProductType'],limit=0,type=2)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp+percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)


                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{new_strike}|CE"
                                # Algofox.Buy_order_algofox(symbol, quantity=params["Quantity"],
                                #                           instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                           strategy=params["STRATEGYTAG"],
                                #                           order_typ="MARKET", price=0, username=Algofoxid,
                                #                           password=Algofoxpassword, role=role,
                                #                           trigger=None, sll_price=None)
                                Orderlog = f"{timestamp} Downside level @ {params['SYMBOL']} trade: {params['TYPE']} entry call strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)
                                lowest_strike = min(params['putstrike'])
                                new_strike = int(lowest_strike - params['STRIKE STEP'])
                                params['putstrike'].append(new_strike)
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=new_strike, opt_type="PE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=new_strike,
                                                                      opt_type="PE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=1, product=params['ProductType'],limit=0,type=2)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp+percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{new_strike}|PE"
                                # Algofox.Buy_order_algofox(symbol, quantity=params["Quantity"],
                                #                           instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                           strategy=params["STRATEGYTAG"],
                                #                           order_typ="MARKET", price=0, username=Algofoxid,
                                #                           password=Algofoxpassword, role=role,
                                #                           trigger=None, sll_price=None)
                                Orderlog = f"{timestamp} Downside level @ {params['SYMBOL']} trade: {params['TYPE']} entry put strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)

                        if (
                                params['ltp']>=params['UpLevel'] and
                                params['UpLevel'] is not None and
                                params['InitialLevelRun'] is not None and
                                params['TradeCount']<params['CycleCount']
                            ):

                            params['Downlevel'] = params['UpLevel'] - params['STRIKE STEP']
                            params['UpLevel'] = params['UpLevel'] + params['STRIKE STEP']
                            params['PrevLevel']='UpLevel'
                            params['TradeCount'] = params['TradeCount'] + 1
                            if params['TYPE'] == 'SHORT':
                                # exit pos logic
                                strike = min(params['callstrike'])
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="CE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=strike,
                                                                      opt_type="CE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=1, product=params['ProductType'],limit=0,type=2)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp+percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|CE"
                                # Algofox.Cover_order_algofox(symbol, quantity=params["Quantity"],
                                #                            instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                            strategy=params["STRATEGYTAG"],
                                #                            order_typ="MARKET", price=0, username=Algofoxid,
                                #                            password=Algofoxpassword, role=role,
                                #                            trigger=None, sll_price=None)
                                params['callstrike'].remove(strike)
                                Orderlog = f"{timestamp} Upside level @ {params['SYMBOL']} trade: {params['TYPE']} exit call strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)

                                strike = min(params['putstrike'])
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="PE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=strike,
                                                                      opt_type="PE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=1, product=params['ProductType'],limit=0,type=2)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp+percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|PE"
                                # Algofox.Cover_order_algofox(symbol, quantity=params["Quantity"],
                                #                            instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                            strategy=params["STRATEGYTAG"],
                                #                            order_typ="MARKET", price=0, username=Algofoxid,
                                #                            password=Algofoxpassword, role=role,
                                #                            trigger=None, sll_price=None)
                                params['putstrike'].remove(strike)
                                Orderlog = f"{timestamp} Upside level @ {params['SYMBOL']} trade: {params['TYPE']} exit put strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)
                                # opening pos logic
                                highest_strike = max(params['callstrike'])
                                new_strike = highest_strike + params['STRIKE STEP']
                                params['callstrike'].append(new_strike)
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=new_strike, opt_type="CE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=new_strike,
                                                                      opt_type="CE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=-1, product=params['ProductType'],limit=0,type=2)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp-percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{new_strike}|CE"
                                # Algofox.Short_order_algofox(symbol, quantity=params["Quantity"],
                                #                           instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                           strategy=params["STRATEGYTAG"],
                                #                           order_typ="MARKET", price=0, username=Algofoxid,
                                #                           password=Algofoxpassword, role=role,
                                #                           trigger=None, sll_price=None)
                                Orderlog = f"{timestamp} Upside level @ {params['SYMBOL']} trade: {params['TYPE']} entry call strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)

                                highest_strike = max(params['putstrike'])
                                new_strike = int(highest_strike + params['STRIKE STEP'])
                                params['putstrike'].append(new_strike)
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=new_strike, opt_type="PE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=new_strike,
                                                                      opt_type="PE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=-1, product=params['ProductType'],limit=0,type=2)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp-percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{new_strike}|PE"
                                # Algofox.Short_order_algofox(symbol, quantity=params["Quantity"],
                                #                           instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                           strategy=params["STRATEGYTAG"],
                                #                           order_typ="MARKET", price=0, username=Algofoxid,
                                #                           password=Algofoxpassword, role=role,
                                #                           trigger=None, sll_price=None)
                                Orderlog = f"{timestamp} Upside level @ {params['SYMBOL']} trade: {params['TYPE']} entry put strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)

                            if params['TYPE'] == 'BUY':
                                # exit pos logic
                                strike= min(params['callstrike'])
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="CE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=strike,
                                                                      opt_type="CE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=-1, product=params['ProductType'],limit=0,type=2)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp-percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|CE"
                                # Algofox.Sell_order_algofox(symbol, quantity=params["Quantity"],
                                #                               instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                               strategy=params["STRATEGYTAG"],
                                #                               order_typ="MARKET", price=0, username=Algofoxid,
                                #                               password=Algofoxpassword, role=role,
                                #                               trigger=None, sll_price=None)
                                params['callstrike'].remove(strike)
                                Orderlog = f"{timestamp} Upside level @ {params['SYMBOL']} trade: {params['TYPE']} exit call strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)

                                strike = min(params['putstrike'])
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=strike, opt_type="PE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=strike,
                                                                      opt_type="PE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=-1, product=params['ProductType'],limit=0,type=2)

                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp-percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{strike}|PE"
                                # Algofox.Sell_order_algofox(symbol, quantity=params["Quantity"],
                                #                            instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                            strategy=params["STRATEGYTAG"],
                                #                            order_typ="MARKET", price=0, username=Algofoxid,
                                #                            password=Algofoxpassword, role=role,
                                #                            trigger=None, sll_price=None)
                                params['putstrike'].remove(strike)
                                Orderlog = f"{timestamp} Upside level @ {params['SYMBOL']} trade: {params['TYPE']} exit put strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)
                                # opening pos logic
                                highest_strike = max(params['callstrike'])
                                new_strike = highest_strike + params['STRIKE STEP']
                                params['callstrike'].append(new_strike)
                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=new_strike, opt_type="CE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=new_strike,
                                                                      opt_type="CE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=1, product=params['ProductType'],limit=0,type=2)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp+percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{new_strike}|CE"
                                # Algofox.Buy_order_algofox(symbol, quantity=params["Quantity"],
                                #                           instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                           strategy=params["STRATEGYTAG"],
                                #                           order_typ="MARKET", price=0, username=Algofoxid,
                                #                           password=Algofoxpassword, role=role,
                                #                           trigger=None, sll_price=None)
                                Orderlog = f"{timestamp} Upside level @ {params['SYMBOL']} trade: {params['TYPE']} entry call strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)

                                highest_strike = max(params['putstrike'])
                                new_strike = int(highest_strike + params['STRIKE STEP'])
                                params['putstrike'].append(new_strike)

                                if params['ContractType'] == "MONTHLY":
                                    symbol = monthly_exp_contract_date(date_str=params['TradeExp'],
                                                                       ex=segment,
                                                                       ex_underlying_symbol=params['BaseSymBol'],
                                                                       strike=new_strike, opt_type="PE")

                                if params['ContractType'] == "WEEKLY":
                                    symbol = weekly_exp_contract_date(date_str=params['TradeExp'], ex=segment,
                                                                      ex_underlying_symbol=params['BaseSymBol'],
                                                                      strike=new_strike,
                                                                      opt_type="PE")
                                if params['LmtPercentage'] == 0:
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=1, product=params['ProductType'],limit=0,type=2)
                                if params['LmtPercentage'] > 0:
                                    lp = next((item['v']['lp'] for item in FyresIntegration.fyres_quote_ltp(symbol).get('d', []) if 'v' in item and 'lp' in item['v']), None)
                                    percentage_value=calculate_percentage(lp,params['LmtPercentage'])
                                    ep=lp+percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)
                                # symbol = f"{params['SYMBOL']}|{params['trade_exp']}|{new_strike}|PE"
                                # Algofox.Buy_order_algofox(symbol, quantity=params["Quantity"],
                                #                           instrumentType='OTPIDX', direction='BUY', product='MIS',
                                #                           strategy=params["STRATEGYTAG"],
                                #                           order_typ="MARKET", price=0, username=Algofoxid,
                                #                           password=Algofoxpassword, role=role,
                                #                           trigger=None, sll_price=None)
                                Orderlog = f"{timestamp} Upside level @ {params['SYMBOL']} trade: {params['TYPE']} entry put strike  {symbol}"
                                print(Orderlog)
                                write_to_order_logs(Orderlog)\

                    print(f"{timestamp} {params['SYMBOL']}: {ltp} : InitialAtm: {params['InitialAtm']}: UpLevel: {params['UpLevel']}: Downlevel: {params['Downlevel']},"
                                f"InitialLevelRun:{params['InitialLevelRun']}, callstrike: {params['callstrike']}, putstrike: {params['putstrike']}")



                if params['TimeBasedExit'] == "TAKEEXIT" and params['TradeCount']==params['CycleCount']:
                    params['TimeBasedExit'] = "EXITDONE"
                    params['TradeCount']=params['CycleCount']+10
                    # Process each strike in callstrike list
                    symbols_string = generate_symbols_string_ce(params, segment=segment)
                    print("symbols_string: ", symbols_string)
                    quote_res = FyresIntegration.fyres_quote_ltp(symbols_string)
                    symbol_to_lp = {item['n']: item['v']['lp'] for item in quote_res['d']}
                    print("quote_res: ", quote_res)
                    for strike in params['callstrike']:
                        if params['ContractType'] == "MONTHLY":
                            symbol = monthly_exp_contract_date(
                                date_str=params['TradeExp'],
                                ex=segment,
                                ex_underlying_symbol=params['BaseSymBol'],
                                strike=strike,
                                opt_type="CE"  # Assuming CE for call strikes
                            )
                        elif params['ContractType'] == "WEEKLY":
                            symbol = weekly_exp_contract_date(
                                date_str=params['TradeExp'],
                                ex=segment,
                                ex_underlying_symbol=params['BaseSymBol'],
                                strike=strike,
                                opt_type="CE"  # Assuming CE for call strikes
                            )
                        # Log the exit and execute the order
                        Orderlog = f"{timestamp} Time-based exit for call strike {symbol}"
                        print(Orderlog)
                        write_to_order_logs(Orderlog)
                        if params['TYPE'] == 'BUY':
                            if params['LmtPercentage'] == 0:
                                FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"], side=-1,
                                                                product=params['ProductType'],limit=0,type=2)

                            if params['LmtPercentage'] > 0:
                                if symbol in symbol_to_lp:
                                    lp_value = symbol_to_lp[symbol]
                                    percentage_value = calculate_percentage(lp_value, params['LmtPercentage'])
                                    ep = lp_value - percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)

                        if params['TYPE'] == 'SHORT':
                            if params['LmtPercentage'] == 0:
                                FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"], side=1,
                                                                product=params['ProductType'],limit=0,type=2)
                            if params['LmtPercentage'] > 0:
                                if symbol in symbol_to_lp:
                                    lp_value = symbol_to_lp[symbol]
                                    percentage_value = calculate_percentage(lp_value, params['LmtPercentage'])
                                    ep = lp_value + percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)

                    # Process each strike in putstrike list
                    symbols_string = generate_symbols_string_pe(params, segment=segment)
                    print("symbols_string: ", symbols_string)
                    quote_res = FyresIntegration.fyres_quote_ltp(symbols_string)
                    symbol_to_lp = {item['n']: item['v']['lp'] for item in quote_res['d']}
                    print("symbol_to_lp: ", symbol_to_lp)
                    for strike in params['putstrike']:
                        if params['ContractType'] == "MONTHLY":
                            symbol = monthly_exp_contract_date(
                                date_str=params['TradeExp'],
                                ex=segment,
                                ex_underlying_symbol=params['BaseSymBol'],
                                strike=strike,
                                opt_type="PE"  # Assuming PE for put strikes
                            )
                        elif params['ContractType'] == "WEEKLY":
                            symbol = weekly_exp_contract_date(
                                date_str=params['TradeExp'],
                                ex=segment,
                                ex_underlying_symbol=params['BaseSymBol'],
                                strike=strike,
                                opt_type="PE"  # Assuming PE for put strikes
                            )
                        # Log the exit and execute the order
                        Orderlog = f"{timestamp} Time-based exit for put strike {symbol}"
                        print(Orderlog)
                        write_to_order_logs(Orderlog)
                        if params['TYPE'] == 'BUY':
                            if params['LmtPercentage'] == 0:
                                FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"], side=-1,
                                                                product=params['ProductType'],limit=0,type=2)

                            if params['LmtPercentage'] > 0:
                                if symbol in symbol_to_lp:
                                    lp_value = symbol_to_lp[symbol]
                                    percentage_value = calculate_percentage(lp_value, params['LmtPercentage'])
                                    ep = lp_value - percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)

                        if params['TYPE'] == 'SHORT':
                            if params['LmtPercentage'] == 0:
                                FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"], side=1,
                                                                product=params['ProductType'],limit=0,type=2)

                            if params['LmtPercentage'] > 0:
                                if symbol in symbol_to_lp:
                                    lp_value = symbol_to_lp[symbol]
                                    percentage_value = calculate_percentage(lp_value, params['LmtPercentage'])
                                    ep = lp_value + percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)



                if current_time.strftime("%H:%M") > ExitTime.strftime("%H:%M") and params[
                    'TimeBasedExit'] == "TAKEEXIT":
                    # Mark the exit as done
                    params['TimeBasedExit'] = "EXITDONE"

                    symbols_string = generate_symbols_string_ce(params, segment=segment)
                    print("symbols_string: ", symbols_string)
                    quote_res = FyresIntegration.fyres_quote_ltp(symbols_string)
                    symbol_to_lp = {item['n']: item['v']['lp'] for item in quote_res['d']}
                    print("quote_res: ", quote_res)
                    for strike in params['callstrike']:
                        if params['ContractType'] == "MONTHLY":
                            symbol = monthly_exp_contract_date(
                                date_str=params['TradeExp'],
                                ex=segment,
                                ex_underlying_symbol=params['BaseSymBol'],
                                strike=strike,
                                opt_type="CE"  # Assuming CE for call strikes
                            )
                        elif params['ContractType'] == "WEEKLY":
                            symbol = weekly_exp_contract_date(
                                date_str=params['TradeExp'],
                                ex=segment,
                                ex_underlying_symbol=params['BaseSymBol'],
                                strike=strike,
                                opt_type="CE"  # Assuming CE for call strikes
                            )
                        # Log the exit and execute the order
                        Orderlog = f"{timestamp} Time-based exit for call strike {symbol}"
                        print(Orderlog)
                        write_to_order_logs(Orderlog)
                        if params['TYPE'] == 'BUY':
                            if params['LmtPercentage'] == 0:
                                FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"], side=-1,
                                                            product=params['ProductType'],limit=0,type=2)

                            if params['LmtPercentage'] > 0:
                                if symbol in symbol_to_lp:
                                    lp_value = symbol_to_lp[symbol]
                                    percentage_value = calculate_percentage(lp_value, params['LmtPercentage'])
                                    ep = lp_value - percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=-1, product=params['ProductType'], type=1,
                                                                    limit=ep)

                        if params['TYPE'] == 'SHORT':
                            if params['LmtPercentage'] == 0:
                                FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"], side=1,
                                                            product=params['ProductType'],limit=0,type=2)
                            if params['LmtPercentage'] > 0:
                                if symbol in symbol_to_lp:
                                    lp_value = symbol_to_lp[symbol]
                                    percentage_value = calculate_percentage(lp_value, params['LmtPercentage'])
                                    ep = lp_value + percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                    side=1, product=params['ProductType'], type=1,
                                                                    limit=ep)

                    # Process each strike in putstrike list
                    symbols_string = generate_symbols_string_pe(params, segment=segment)
                    print("symbols_string: ", symbols_string)
                    quote_res = FyresIntegration.fyres_quote_ltp(symbols_string)
                    symbol_to_lp = {item['n']: item['v']['lp'] for item in quote_res['d']}
                    print("symbol_to_lp: ", symbol_to_lp)
                    for strike in params['putstrike']:
                        if params['ContractType'] == "MONTHLY":
                            symbol = monthly_exp_contract_date(
                                date_str=params['TradeExp'],
                                ex=segment,
                                ex_underlying_symbol=params['BaseSymBol'],
                                strike=strike,
                                opt_type="PE"  # Assuming PE for put strikes
                            )
                        elif params['ContractType'] == "WEEKLY":
                            symbol = weekly_exp_contract_date(
                                date_str=params['TradeExp'],
                                ex=segment,
                                ex_underlying_symbol=params['BaseSymBol'],
                                strike=strike,
                                opt_type="PE"  # Assuming PE for put strikes
                            )
                        # Log the exit and execute the order
                        Orderlog = f"{timestamp} Time-based exit for put strike {symbol}"
                        print(Orderlog)
                        write_to_order_logs(Orderlog)
                        if params['TYPE'] == 'BUY':
                            if params['LmtPercentage'] == 0:
                                FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"], side=-1,
                                                                product=params['ProductType'],limit=0,type=2)
                            if params['LmtPercentage'] > 0:
                                if symbol in symbol_to_lp:
                                    lp_value = symbol_to_lp[symbol]
                                    percentage_value = calculate_percentage(lp_value, params['LmtPercentage'])
                                    ep = lp_value - percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=-1, product=params['ProductType'], type=1,
                                                                        limit=ep)

                        if params['TYPE'] == 'SHORT':
                            if params['LmtPercentage'] == 0:
                                FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"], side=1,
                                                                product=params['ProductType'],limit=0,type=2)
                            if params['LmtPercentage'] > 0:
                                if symbol in symbol_to_lp:
                                    lp_value = symbol_to_lp[symbol]
                                    percentage_value = calculate_percentage(lp_value, params['LmtPercentage'])
                                    ep = lp_value + percentage_value
                                    ep = int(ep) + 0.05
                                    FyresIntegration.fyers_single_order(symbol=symbol, qty=params["Quantity"],
                                                                        side=1, product=params['ProductType'], type=1,
                                                                        limit=ep)






    except Exception as e:
        print("Error in main strategy : ", str(e))
        traceback.print_exc()




while True:
    print("Main Strategy while loop running ")
    main_strategy()
    time.sleep(2)

