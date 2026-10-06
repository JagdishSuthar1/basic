import time
from fastapi import Body, Depends, FastAPI, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

class InsufficientBalanceError(Exception):
    def __init__(self,msg):
        self.msg = msg
        super().__init__(self.msg)

@app.exception_handler(InsufficientBalanceError)
def handler(request,exc):
    return JSONResponse(
        status_code=404,
        content = {
            "error" : exc.msg
        }
    )



class BankAccount:
    def __init__(self,account_number, balance, name):
        self.account_number = account_number
        self.balance = balance
        self.name = name

    def getBalance(self):
        return self.balance

    def info(self):
        print(f"Account Number: {self.account_number}, Balance: {self.balance}, Name: {self.name}")
        return

    def deposit(self,amount):
        if(amount < 0):
            raise ValueError("Amount must be positive")
        else:
            self.balance = self.balance + amount

    def withdraw(self, amount):
        if(amount > self.balance):
            raise InsufficientBalanceError("Insufficient balance")
        else:
            self.balance = self.balance - amount


class pydanticAccountModel(BaseModel):
    name : str
    balance : int


accounts : list[BankAccount] = []

print("changes in main branch")
@app.post("/accounts")
async def create_account(request : Request,account: pydanticAccountModel):
    length = len(accounts)
    print(f"reqeust body : {await request.body()}")
    new_account = BankAccount(account_number=length, balance = account.balance, name = account.name)
    accounts.append(new_account)
    return {"message" : "Account created successfully", "data" : new_account}

def time_middleware(request : Request):
    print("Request reached", time.time())

    yield
    print("Request completed", time.time())



@app.get("/accounts/{account_number}",dependencies=[Depends(time_middleware)])
def get_account(request: Request,account_number :int):
    headers = request.headers
    print(f"headers : {headers}")
    return accounts[account_number]

@app.post("/accounts/{account_number}/deposit")
def deposit(account_number : int, balance : int = Body(...,embed=True)):
    accounts[account_number].deposit(balance)
    return {"message" : "Deposit successful"}

@app.post("/accounts/{account_number}/withdraw")
def withdraw(account_number : int, balance : int = Body(...,embed=True)):
    try:
        accounts[account_number].withdraw(balance)
    except InsufficientBalanceError as e:
        return {"error" : e.msg}
    return {"message" : "Withdrawal successful"}