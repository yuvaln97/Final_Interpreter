import re


class ScriptInterpreter:
    def __init__(self):
        self.variables = {}

    def evaluate_expression(self, expression):
        tokens = re.findall(r'\d+|\+|\-|\*|\/|\(|\)|[a-zA-Z_]\w*|==|!=|<=|>=|<|>|and|or|not', expression)
        operator_stack = []
        operand_stack = []

        for token in tokens:
            if token.isdigit():
                operand_stack.append(int(token))
            elif token in self.variables:
                operand_stack.append(self.variables[token])
            elif token in ['+', '-', '*', '/', '==', '!=', '<=', '>=', '<', '>', 'and', 'or', 'not']:
                while (operator_stack and
                       self.precedence(operator_stack[-1]) >= self.precedence(token)):
                    self.apply_operation(operator_stack.pop(), operand_stack)
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack[-1] != '(':
                    self.apply_operation(operator_stack.pop(), operand_stack)
                operator_stack.pop()

        while operator_stack:
            self.apply_operation(operator_stack.pop(), operand_stack)

        if operand_stack:
            return operand_stack[0]  # Return the result if the operand stack is not empty
        else:
            return None  # Return None if the operand stack is empty

    def precedence(self, op):
        if op in ['+', '-']:
            return 1
        elif op in ['*', '/']:
            return 2
        elif op in ['==', '!=', '<=', '>=', '<', '>', 'and', 'or', 'not']:
            return 3
        else:
            return 0

    def apply_operation(self, op, operand_stack):
        if op == 'and':
            operand_stack.append(operand_stack.pop() and operand_stack.pop())
        elif op == 'or':
            operand_stack.append(operand_stack.pop() or operand_stack.pop())
        elif op == 'not':
            operand_stack.append(not operand_stack.pop())
        else:
            b = operand_stack.pop()
            a = operand_stack.pop()
            if op == '+':
                operand_stack.append(a + b)
            elif op == '-':
                operand_stack.append(a - b)
            elif op == '*':
                operand_stack.append(a * b)
            elif op == '/':
                if b == 0:
                    print("You can't divide by 0")
                else:
                    operand_stack.append(a / b)
            elif op == '==':
                operand_stack.append(a == b)
            elif op == '!=':
                operand_stack.append(a != b)
            elif op == '<=':
                operand_stack.append(a <= b)
            elif op == '>=':
                operand_stack.append(a >= b)
            elif op == '<':
                operand_stack.append(a < b)
            elif op == '>':
                operand_stack.append(a > b)

    def interpret(self, code):
        lines = code.split('\n')
        output = []
        try:
            if_num = 0
            for line in lines:
                if line.startswith('IF'):
                    parts = re.split(r'\sTHEN\s', line.strip())
                    for part in parts:
                        if 'IF' in part:
                            if_num += 1
                    if if_num > 3:
                        print("Can't support more than 3 nested IF statements")
                        return None
                    elif if_num == 1:
                        condition = parts[0][3:].strip()  # grabbing the condition
                        expr_if = parts[1]
                    else:  # 2 to 3 conditions
                        for index in range(if_num):
                            current_condition = parts[index][3:].strip()
                            if not self.evaluate_expression(current_condition):
                                if not parts[len(parts) - index - 1].isdigit():
                                    exec(parts[len(parts) - index - 1])
                                else:
                                    return parts[len(parts) - index - 1]
                            if index != if_num - 1:
                                pass
                            else:  # Condition is true
                                if not parts[len(parts) - index - 2].isdigit():
                                    exec(parts[len(parts) - index - 2])
                                else:
                                    return parts[len(parts) - index - 2]

                    # Handle 'AND/OR' in conditions
                    if 'AND' in condition:
                        cond_parts = condition.split('AND')
                        condition = '(' + cond_parts[0].strip() + ') and (' + cond_parts[1].strip() + ')'
                    elif 'OR' in condition:
                        cond_parts = condition.split('OR')
                        condition = '(' + cond_parts[0].strip() + ') or (' + cond_parts[1].strip() + ')'

                    if self.evaluate_expression(condition):
                        result = self.evaluate_expression(expr_if)
                        output.append(result)
                        return result
                    else:
                        return None

                elif '=' in line or '==' in line or '>' in line or '<' in line:
                    num_length = 0
                    var_length = 0
                    var_list = []
                    separated_line = line.split('=')
                    for expression in separated_line:
                        if expression.isalpha() and expression not in self.variables:
                            var_length += 1
                        elif expression in self.variables:
                            var_length += 1
                            var_list.append(expression)
                        elif expression.isdigit():
                            num_length += 1
                        elif '+' or '-' or '*' or '/' in expression:  # limited to 1 operation only for Example: x=x+2,x=x*2 etc
                            var_calc = 0
                            num_calc = 0

                            if '+' in expression:
                                for arg in expression:
                                    if arg in self.variables:
                                        var_calc += 1
                                        var_list.append(arg)
                                    elif arg.isdigit():
                                        num_calc += 1
                                        num_op = arg
                            if num_calc == 1 and var_calc == 1:
                                self.variables[var_list[0]] += int(num_op)
                                return self.variables[var_list[0]]
                            elif var_calc == 2:
                                if len(var_list) == 3:
                                    try:
                                        self.variables[var_list[0]] = self.variables[var_list[1]] + self.variables[
                                            var_list[2]]
                                        return self.variables[var_list[0]]
                                    except Exception as e:
                                        print("Unsupported Action: ", e)
                            elif '-' in expression:
                                for arg in expression:
                                    if arg in self.variables:
                                        var_calc += 1
                                        var_list.append(arg)
                                    elif arg.isdigit():
                                        num_calc += 1
                                        num_op = arg
                                if num_calc == 1 and var_calc == 1:
                                    self.variables[var_list[0]] -= int(num_op)
                                    return self.variables[var_list[0]]
                                elif var_calc == 2:
                                    if len(var_list) == 3:
                                        try:
                                            self.variables[var_list[0]] = self.variables[var_list[1]] - self.variables[
                                                var_list[2]]
                                            return self.variables[var_list[0]]
                                        except Exception as e:
                                            print("Unsupported Action: ", e)
                            elif '*' in expression:
                                for arg in expression:
                                    if arg in self.variables:
                                        var_calc += 1
                                        var_list.append(arg)
                                    elif arg.isdigit():
                                        num_calc += 1
                                        num_op = arg
                                if num_calc == 1 and var_calc == 1:
                                    self.variables[var_list[0]] *= int(num_op)
                                    return self.variables[var_list[0]]
                                elif var_calc == 2:
                                    if len(var_list) == 3:
                                        try:
                                            self.variables[var_list[0]] = self.variables[var_list[1]] * self.variables[
                                                var_list[2]]
                                            return self.variables[var_list[0]]
                                        except Exception as e:
                                            print("Unsupported Action: ", e)

                            elif '/' in expression:
                                for arg in expression:
                                    if arg in self.variables:
                                        var_calc += 1
                                        var_list.append(arg)
                                    elif arg.isdigit():
                                        num_calc += 1
                                        num_op = arg
                                if num_calc == 1 and var_calc == 1:
                                    self.variables[var_list[0]] /= int(num_op)
                                    return self.variables[var_list[0]]
                                elif var_calc == 2:
                                    if len(var_list) == 3:
                                        try:
                                            if self.variables[var_list[2]] != 0:

                                                self.variables[var_list[0]] = self.variables[var_list[1]] / \
                                                                              self.variables[
                                                                                  var_list[2]]
                                                return self.variables[var_list[0]]
                                            else:
                                                print("you can't divide by zero")
                                        except Exception as e:
                                            print("Unsupported Action: ", e)

                    if num_length == 2:
                        num1, num2 = line.split('=')
                        return int(num1) == int(num2)
                    elif var_length == 2:
                        var1_name, var2_name = line.split('=')
                        if var1_name in self.variables and var2_name in self.variables:
                            return self.variables[var1_name] == self.variables[var2_name]
                        elif var1_name not in self.variables:
                            print(f'{var1_name} not defined')
                        elif var2_name not in self.variables:
                            print(f'{var2_name} not defined')
                    elif var_length >= 3 or num_length == 3:
                        print("Can't compare between 3 Arguments Or Numbers")
                    else:
                        var_name, expr = line.split('=')
                        var_name = var_name.strip()
                        expr = expr.strip()
                        self.variables[var_name] = self.evaluate_expression(expr)

                elif '>' in line:
                    num_length = 0
                    var_length = 0
                    separated_line = line.split('>')
                    for num in separated_line:
                        if not num.isdigit():
                            var_length += 1
                        else:
                            num_length += 1
                    if num_length == 2:
                        num1, num2 = line.split('>')
                        return int(num1) > int(num2)
                    elif var_length == 2:
                        var1_name, var2_name = line.split('>')
                        if var1_name in self.variables and var2_name in self.variables:
                            return self.variables[var1_name] > self.variables[var2_name]
                        elif var1_name not in self.variables:
                            print(f'{var1_name} not defined')
                        elif var2_name not in self.variables:
                            print(f'{var2_name} not defined')
                    elif var_length >= 3 or num_length == 3:
                        print("Can't compare between 3 Arguments Or Numbers")
                    elif var_length == 1 and num_length == 1:
                        arg1, arg2 = line.split('>')
                        if arg1 in self.variables:
                            return self.variables[arg1] > int(arg2)
                        else:
                            return int(arg1) > self.variables[arg2]

                elif '<' in line:
                    num_length = 0
                    var_length = 0
                    separated_line = line.split('<')
                    for num in separated_line:
                        if not num.isdigit():
                            var_length += 1
                        else:
                            num_length += 1
                    if num_length == 2:
                        num1, num2 = line.split('<')
                        return int(num1) < int(num2)
                    elif var_length == 2:
                        var1_name, var2_name = line.split('<')
                        if var1_name in self.variables and var2_name in self.variables:
                            return self.variables[var1_name] < self.variables[var2_name]
                        elif var1_name not in self.variables:
                            print(f'{var1_name} not defined')
                        elif var2_name not in self.variables:
                            print(f'{var2_name} not defined')
                    elif var_length >= 3 or num_length == 3:
                        print("Can't compare between 3 Arguments Or Numbers")
                    elif var_length == 1 and num_length == 1:
                        arg1, arg2 = line.split('<')
                        if arg1 in self.variables:
                            return self.variables[arg1] < int(arg2)  # arg1 is variable arg2 is number
                        else:
                            return int(arg1) < self.variables[arg2]  # arg1 is number arg2 is variable
                else:
                    result = self.evaluate_expression(line)
                    return result
        except Exception as e:
            print(f"Exception: {e}")
            return None


if __name__ == "__main__":
    interpreter = ScriptInterpreter()
    try:
        while True:
            code = input(">> ")
            if code == "exit":
                break
            output = interpreter.interpret(code)
            if output is not None:
                print(output)
        print("Thank you for using our cool interpreter!")

    except KeyboardInterrupt:
        print("Thank you for using our cool interpreter!")
