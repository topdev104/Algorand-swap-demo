from typing import Tuple

from algosdk.v2client.algod import AlgodClient
from pyteal import *

from utils import fully_compile_contract


class SwapContract:
    def on_create(self):
        return Seq(
            Approve()
        )

    def on_call(self):
        on_call_method = Txn.application_args[0]
        return Cond(

        )

    def on_delete(self):
        return Seq(
            Approve()
        )

    def approval_program(self):
        program = Cond(
            [Txn.application_id() == Int(0), self.on_create()],
            [Txn.on_completion() == OnComplete.NoOp, self.on_call()],
            [
                Txn.on_completion() == OnComplete.DeleteApplication,
                self.on_delete(),
            ],
            [
                Or(
                    Txn.on_completion() == OnComplete.OptIn,
                    Txn.on_completion() == OnComplete.CloseOut,
                    Txn.on_completion() == OnComplete.UpdateApplication,
                ),
                Reject(),
            ],
        )
        return program

    def clear_state_program(self):
        return Approve()

    @staticmethod
    def get_contracts(client: AlgodClient) -> Tuple[bytes, bytes]:
        trading_contract = SwapContract()
        approval_program = b""
        clear_state_program = b""

        if len(approval_program) == 0:
            approval_program = fully_compile_contract(client, trading_contract.approval_program())
            clear_state_program = fully_compile_contract(client, trading_contract.clear_state_program())

        return approval_program, clear_state_program

    @staticmethod
    def compile_contracts():
        trading_contract = SwapContract()
        with open("trading_approval.teal", "w") as f:
            compiled = compileTeal(trading_contract.approval_program(), mode=Mode.Application, version=5)
            f.write(compiled)

        with open("trading_clear_state.teal", "w") as f:
            compiled = compileTeal(trading_contract.clear_state_program(), mode=Mode.Application, version=5)
            f.write(compiled)


if __name__ == "__main__":
    SwapContract.compile_contracts()
