from Tutel.common.ErrorType import NotIterableException


class Stack(list):
    pass


if __name__ == '__main__':
    from Tutel.core.InterpreterModule.StackFrame import StackFrame
    from Tutel.core.InterpreterModule.Value import Value
    import json

    test = [StackFrame("main", 23)]
    test[-1].locals["var"] = Value(25)
    test.append(StackFrame("boo", 1))
    print(json.dumps({"event": "stack_trace", "body": {"stack": test}}))

    e = NotIterableException(str)
    print(json.dumps({"event": "post_mortem", "body": {"error": str(e)}}))
