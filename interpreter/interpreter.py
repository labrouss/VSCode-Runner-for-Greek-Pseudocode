#!/usr/bin/env python3
"""
EAP Pseudocode Interpreter - Complete CLI Version
Single file, no dependencies, just works!

Usage:
    python interpreter.py program.eap
    python interpreter.py program.eap --debug

Author: Based on EAP PLH10 specification
"""

import sys
import unicodedata
from typing import List, Dict, Any, Optional, Union
from enum import Enum, auto
from dataclasses import dataclass, field


# =============================================================================
# TOKENIZER
# =============================================================================

class TokenType(Enum):
    # Structure
    ALGORITHM = auto()
    CONSTANTS = auto()
    DATA = auto()
    BEGIN = auto()
    END = auto()
    
    # Subroutines
    PROCEDURE = auto() 
    FUNCTION = auto() 
    INTERFACE = auto() 
    INPUT_PARAM = auto() 
    OUTPUT_PARAM = auto() 
    END_FUNCTION = auto() # ΤΕΛΟΣ-ΣΥΝΑΡΤΗΣΗΣ
    END_PROCEDURE = auto() # ΤΕΛΟΣ-ΔΙΑΔΙΚΑΣΙΑΣ
    
    # Control Flow
    IF = auto()
    THEN = auto()
    ELSE = auto()
    END_IF = auto() # ΕΑΝ-ΤΕΛΟΣ
    FOR = auto()
    TO = auto()
    STEP = auto()
    REPEAT = auto()
    END_FOR = auto() # ΓΙΑ-ΤΕΛΟΣ
    WHILE = auto()
    END_WHILE = auto() # ΕΝΟΣΩ-ΤΕΛΟΣ
    UNTIL = auto()
    
    # I/O
    PRINT = auto()
    READ = auto()
    CALCULATE = auto()
    
    # Data Types
    INTEGER_TYPE = auto()
    REAL_TYPE = auto()
    BOOLEAN_TYPE = auto()
    CHAR_TYPE = auto()
    STRING_TYPE = auto()
    ARRAY = auto()
    OF = auto()
    
    # Operators
    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MOD = auto()
    DIV = auto()
    
    # Comparison
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUALS = auto()
    GREATER_EQUALS = auto()
    
    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()
    # Boolean Literal Type
    BOOLEAN_LITERAL = auto()
    
    # Punctuation
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    DOT = auto()
    PERCENT = auto()
    
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int


def remove_accents(text: str) -> str:
    """Remove Greek accents for keyword matching"""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')


# Greek and English keywords
# Χρησιμοποιούμε τις επίσημες λέξεις-κλειδιά με παύλα (ΕΑΝ-ΤΕΛΟΣ, κλπ.)
KEYWORDS = {
    # Structure
    'ΑΛΓΟΡΙΘΜΟΣ': TokenType.ALGORITHM, 'ΣΤΑΘΕΡΕΣ': TokenType.CONSTANTS,
    'ΔΕΔΟΜΕΝΑ': TokenType.DATA, 'ΑΡΧΗ': TokenType.BEGIN, 'ΤΕΛΟΣ': TokenType.END,
    
    # Subroutines
    'ΣΥΝΑΡΤΗΣΗ': TokenType.FUNCTION, 'ΔΙΑΔΙΚΑΣΙΑ': TokenType.PROCEDURE,
    'ΔΙΕΠΑΦΗ': TokenType.INTERFACE, 
    'ΕΙΣΟΔΟΣ': TokenType.INPUT_PARAM, # Greek keyword for "INPUT parameter"
    'ΕΞΟΔΟΣ': TokenType.OUTPUT_PARAM, # Greek keyword for "OUTPUT parameter"
    'ΤΕΛΟΣ-ΣΥΝΑΡΤΗΣΗΣ': TokenType.END_FUNCTION, 'ΤΕΛΟΣ-ΔΙΑΔΙΚΑΣΙΑΣ': TokenType.END_PROCEDURE, 
    
    # Control Flow
    'ΕΑΝ': TokenType.IF, 'ΤΟΤΕ': TokenType.THEN, 'ΑΛΛΙΩΣ': TokenType.ELSE,
    'ΕΑΝ-ΤΕΛΟΣ': TokenType.END_IF, 'ΓΙΑ': TokenType.FOR, 'ΕΩΣ': TokenType.TO,
    'ΜΕ': TokenType.STEP, 'ΒΗΜΑ': TokenType.STEP, 'ΕΠΑΝΑΛΑΒΕ': TokenType.REPEAT,
    'ΓΙΑ-ΤΕΛΟΣ': TokenType.END_FOR, 'ΕΝΟΣΩ': TokenType.WHILE, 
    'ΕΝΟΣΩ-ΤΕΛΟΣ': TokenType.END_WHILE, 'ΜΕΧΡΙ': TokenType.UNTIL,
    
    # I/O
    'ΤΥΠΩΣΕ': TokenType.PRINT, 'ΔΙΑΒΑΣΕ': TokenType.READ,
    'ΥΠΟΛΟΓΙΣΕ': TokenType.CALCULATE,
    
    # Data Types
    'ΑΚΕΡΑΙΟΣ': TokenType.INTEGER_TYPE, 'ΠΡΑΓΜΑΤΙΚΟΣ': TokenType.REAL_TYPE,
    'ΛΟΓΙΚΟΣ': TokenType.BOOLEAN_TYPE, 'ΧΑΡΑΚΤΗΡΑΣ': TokenType.CHAR_TYPE,
    'ΣΥΜΒΟΛΟΣΕΙΡΑ': TokenType.STRING_TYPE, 'ΚΑΙ': TokenType.AND,
    'Ή': TokenType.OR, 'ΟΧΙ': TokenType.NOT,
    
    # NEW: Boolean Literals
    'ΑΛΗΘΗΣ': TokenType.BOOLEAN_LITERAL, 
    'ΨΕΥΔΗΣ': TokenType.BOOLEAN_LITERAL,
    
    # English equivalents (for robustness) - Removed INPUT/OUTPUT to allow them as identifiers
    'ALGORITHM': TokenType.ALGORITHM, 'CONSTANTS': TokenType.CONSTANTS,
    'DATA': TokenType.DATA, 'BEGIN': TokenType.BEGIN, 'END': TokenType.END,
    'FUNCTION': TokenType.FUNCTION, 'PROCEDURE': TokenType.PROCEDURE,
    'INTERFACE': TokenType.INTERFACE, 
    # 'INPUT': TokenType.INPUT_PARAM,  <-- REMOVED TO ALLOW "INPUT" AS IDENTIFIER
    # 'OUTPUT': TokenType.OUTPUT_PARAM, <-- REMOVED TO ALLOW "OUTPUT" AS IDENTIFIER
    'END_FUNCTION': TokenType.END_FUNCTION, 'END_PROCEDURE': TokenType.END_PROCEDURE,
    
    'IF': TokenType.IF, 'THEN': TokenType.THEN, 'ELSE': TokenType.ELSE,
    'ENDIF': TokenType.END_IF, 'END_IF': TokenType.END_IF,
    'FOR': TokenType.FOR, 'TO': TokenType.TO, 'STEP': TokenType.STEP,
    'REPEAT': TokenType.REPEAT, 'ENDFOR': TokenType.END_FOR,
    'END_FOR': TokenType.END_FOR, 'WHILE': TokenType.WHILE,
    'ENDWHILE': TokenType.END_WHILE, 'END_WHILE': TokenType.END_WHILE,
    'UNTIL': TokenType.UNTIL, 'PRINT': TokenType.PRINT, 'READ': TokenType.READ,
    'CALCULATE': TokenType.CALCULATE,
    'INTEGER': TokenType.INTEGER_TYPE, 'REAL': TokenType.REAL_TYPE,
    'BOOLEAN': TokenType.BOOLEAN_TYPE, 'CHAR': TokenType.CHAR_TYPE,
    'STRING': TokenType.STRING_TYPE, 'ARRAY': TokenType.ARRAY, 'OF': TokenType.OF,
    'MOD': TokenType.MOD, 'DIV': TokenType.DIV, 'AND': TokenType.AND,
    'OR': TokenType.OR, 'NOT': TokenType.NOT,
    # NEW: Boolean Literals
    'TRUE': TokenType.BOOLEAN_LITERAL,
    'FALSE': TokenType.BOOLEAN_LITERAL,
}

OPERATORS = {
    ':=': TokenType.ASSIGN, '+': TokenType.PLUS, '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY, '/': TokenType.DIVIDE, '=': TokenType.EQUALS,
    '<>': TokenType.NOT_EQUALS, '<=': TokenType.LESS_EQUALS,
    '>=': TokenType.GREATER_EQUALS, '<': TokenType.LESS_THAN,
    '>': TokenType.GREATER_THAN, '(': TokenType.LEFT_PAREN,
    ')': TokenType.RIGHT_PAREN, '[': TokenType.LEFT_BRACKET,
    ']': TokenType.RIGHT_BRACKET, ',': TokenType.COMMA,
    ':': TokenType.COLON, ';': TokenType.SEMICOLON, '..': TokenType.DOT, 
    '%': TokenType.PERCENT,
}


class Tokenizer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

        # Λίστα με τις σύνθετες λέξεις-κλειδιά που περιέχουν παύλα
        self.COMPOUND_KEYWORDS = {
            'ΕΑΝ-ΤΕΛΟΣ': TokenType.END_IF, 
            'ΓΙΑ-ΤΕΛΟΣ': TokenType.END_FOR, 
            'ΕΝΟΣΩ-ΤΕΛΟΣ': TokenType.END_WHILE, 
            'ΤΕΛΟΣ-ΣΥΝΑΡΤΗΣΗΣ': TokenType.END_FUNCTION, 
            'ΤΕΛΟΣ-ΔΙΑΔΙΚΑΣΙΑΣ': TokenType.END_PROCEDURE
        }
    
    def current_char(self) -> Optional[str]:
        return self.code[self.pos] if self.pos < len(self.code) else None
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        pos = self.pos + offset
        return self.code[pos] if pos < len(self.code) else None
    
    def advance(self):
        if self.pos < len(self.code):
            if self.code[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char().isspace():
            self.advance()
    
    def skip_comment(self):
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
            return True
        
        if self.current_char() == '/' and self.peek_char() == '*':
            self.advance()
            self.advance()
            while self.current_char():
                if self.current_char() == '*' and self.peek_char() == '/':
                    self.advance()
                    self.advance()
                    break
                self.advance()
            return True
        
        return False
    
    def read_string(self) -> str:
        value = ''
        self.advance()
        while self.current_char() and self.current_char() != '"':
            value += self.current_char()
            self.advance()
        if self.current_char() == '"':
            self.advance()
        return value
    
    def read_number(self) -> Union[int, float]:
        num_str = ''
        while self.current_char() and self.current_char().isdigit():
            num_str += self.current_char()
            self.advance()
        
        if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
            num_str += self.current_char()
            self.advance()
            while self.current_char() and self.current_char().isdigit():
                num_str += self.current_char()
                self.advance()
            return float(num_str)
        
        return int(num_str)
    
    def read_identifier(self) -> str:
        ident = ''
        while self.current_char() and (
            self.current_char().isalnum() or 
            self.current_char() == '_' or  
            # Ο χαρακτήρας '-' ΔΕΝ επιτρέπεται σε αναγνωριστικά.
            ord(self.current_char()) >= 0x0370
        ):
            ident += self.current_char()
            self.advance()
        return ident
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.code):
            self.skip_whitespace()
            if not self.current_char():
                break
            
            if self.skip_comment():
                continue
            
            start_line, start_col = self.line, self.column
            
            # --- Compound Keyword Check (Lookahead) ---
            # Ελέγχουμε πρώτα για τις σύνθετες λέξεις-κλειδιά με παύλα, 
            # ώστε να μην τις διασπάσει ο κανόνας του τελεστή '-'.
            found_compound = False
            for kw_text, kw_type in self.COMPOUND_KEYWORDS.items():
                # Ελέγχουμε αν το τρέχον σημείο αρχίζει με τη λέξη-κλειδί (αδιαφορώντας για τόνους/πεζά)
                raw_block = self.code[self.pos:self.pos + len(kw_text)]
                if remove_accents(raw_block).upper() == remove_accents(kw_text).upper():
                    
                    # Καταναλώνουμε τους χαρακτήρες
                    for char in raw_block:
                         self.advance()
                         
                    self.tokens.append(Token(kw_type, raw_block, start_line, start_col))
                    found_compound = True
                    break
            
            if found_compound:
                continue

            # --- String / Number / Operator / Identifier Checks ---
            
            if self.current_char() == '"':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, start_line, start_col))
                continue
            
            if self.current_char().isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, start_line, start_col))
                continue
            
            two_char = self.code[self.pos:self.pos+2]
            if two_char in OPERATORS:
                self.advance()
                self.advance()
                self.tokens.append(Token(OPERATORS[two_char], two_char, start_line, start_col))
                continue
            
            if self.current_char() in OPERATORS:
                char = self.current_char()
                self.advance()
                self.tokens.append(Token(OPERATORS[char], char, start_line, start_col))
                continue
            
            if self.current_char().isalpha() or ord(self.current_char()) >= 0x0370:
                ident = self.read_identifier()
                ident_upper = remove_accents(ident.upper())
                
                if ident_upper in KEYWORDS:
                    self.tokens.append(Token(KEYWORDS[ident_upper], ident.upper(), start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, ident, start_line, start_col))
                continue
            
            raise SyntaxError(f"Unexpected '{self.current_char()}' at line {self.line}:{self.column}")
        
        self.tokens.append(Token(TokenType.EOF, 'EOF', self.line, self.column))
        return self.tokens


# =============================================================================
# PARSER & AST (No changes here)
# =============================================================================

@dataclass
class ASTNode:
    type: str
    line: int = 0


@dataclass
class Program(ASTNode):
    name: str = ''
    declarations: List[ASTNode] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class ConstantDeclaration(ASTNode):
    name: str = ''
    value: Optional[ASTNode] = None

@dataclass
class ArrayDimension(ASTNode):
    start: Optional[ASTNode] = None
    end: Optional[ASTNode] = None

@dataclass
class ArrayType(ASTNode):
    base_type: str = ''
    dimensions: List[ArrayDimension] = field(default_factory=list)

@dataclass
class VariableDeclaration(ASTNode):
    name: str = ''
    var_type: Union[str, ArrayType] = None 


@dataclass
class Parameter(ASTNode):
    name: str = ''
    param_type: Union[str, ArrayType] = None
    is_reference: bool = False 

@dataclass
class FunctionDeclaration(ASTNode):
    name: str = ''
    return_type: Union[str, ArrayType] = None
    parameters: List[Parameter] = field(default_factory=list)
    declarations: List[ASTNode] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class ProcedureDeclaration(ASTNode):
    name: str = ''
    parameters: List[Parameter] = field(default_factory=list)
    declarations: List[ASTNode] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class CallExpression(ASTNode):
    name: str = ''
    arguments: List[ASTNode] = field(default_factory=list)
    is_statement: bool = False

@dataclass
class Assignment(ASTNode):
    identifier: str = ''
    indices: List[ASTNode] = field(default_factory=list)
    value: Optional[ASTNode] = None


@dataclass
class PrintStatement(ASTNode):
    expressions: List[ASTNode] = field(default_factory=list)


@dataclass
class ReadStatement(ASTNode):
    variables: List[ASTNode] = field(default_factory=list)  # Changed from List[str]
    
    
@dataclass
class IfStatement(ASTNode):
    condition: Optional[ASTNode] = None
    then_branch: List[ASTNode] = field(default_factory=list)
    else_branch: Optional[List[ASTNode]] = None


@dataclass
class ForLoop(ASTNode):
    variable: str = ''
    start: Optional[ASTNode] = None
    end: Optional[ASTNode] = None
    step: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class WhileLoop(ASTNode):
    condition: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class BinaryOp(ASTNode):
    operator: str = ''
    left: Optional[ASTNode] = None
    right: Optional[ASTNode] = None


@dataclass
class UnaryOp(ASTNode):
    operator: str = ''
    operand: Optional[ASTNode] = None


@dataclass
class Literal(ASTNode):
    value: Any = None


@dataclass
class Identifier(ASTNode):
    name: str = ''


@dataclass
class ArrayAccess(ASTNode):
    name: str = ''
    indices: List[ASTNode] = field(default_factory=list)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]
    
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def expect(self, token_type: TokenType) -> Token:
        token = self.current()
        if token.type != token_type:
            raise SyntaxError(f"Expected {token_type.name} but got {token.type.name} at line {token.line}")
        self.advance()
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        return self.current().type in token_types
    
    def parse(self) -> Program:
        self.expect(TokenType.ALGORITHM)
        name = self.expect(TokenType.IDENTIFIER).value
        
        declarations = []
        
        # 1. Parse CONSTANTS
        if self.match(TokenType.CONSTANTS):
            self.advance()
            while self.match(TokenType.IDENTIFIER):
                line = self.current().line
                name_const = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.EQUALS)
                value_expr = self.parse_expression()
                self.expect(TokenType.SEMICOLON)
                declarations.append(ConstantDeclaration(type='ConstDecl', name=name_const, value=value_expr, line=line))

        # 2. Parse DATA
        if self.match(TokenType.DATA):
            self.advance()
            while self.match(TokenType.IDENTIFIER):
                names = [self.expect(TokenType.IDENTIFIER).value]
                while self.match(TokenType.COMMA):
                    self.advance()
                    names.append(self.expect(TokenType.IDENTIFIER).value)
                self.expect(TokenType.COLON)
                var_type_ast = self.parse_type()
                self.expect(TokenType.SEMICOLON)
                for n in names:
                    declarations.append(VariableDeclaration(type='VarDecl', name=n, var_type=var_type_ast, line=self.current().line))

        # 3. Parse Subroutines (Functions and Procedures)
        while self.match(TokenType.FUNCTION, TokenType.PROCEDURE):
            if self.match(TokenType.FUNCTION):
                declarations.append(self.parse_function())
            else:
                declarations.append(self.parse_procedure())
        
        self.expect(TokenType.BEGIN)
        body = self.parse_block()
        self.expect(TokenType.END)
        
        return Program(type='Program', name=name, declarations=declarations, body=body)
    
    def parse_type(self) -> Union[str, ArrayType]:
        if self.match(TokenType.INTEGER_TYPE, TokenType.REAL_TYPE, TokenType.BOOLEAN_TYPE, TokenType.CHAR_TYPE, TokenType.STRING_TYPE):
            t = self.current().type.name
            self.advance()
            return t
        
        if self.match(TokenType.ARRAY):
            self.advance()
            dimensions = []
            
            self.expect(TokenType.LEFT_BRACKET)
            
            # Loop to parse dimensions: E1..E2, E3..E4, ...
            while True:
                start_expr = self.parse_expression()
                self.expect(TokenType.DOT) 
                end_expr = self.parse_expression()
                
                dim = ArrayDimension(type='ArrDim', start=start_expr, end=end_expr)
                dimensions.append(dim)
                
                if self.match(TokenType.COMMA):
                    self.advance()
                else:
                    break
                    
            self.expect(TokenType.RIGHT_BRACKET)
            self.expect(TokenType.OF)
            
            base_type = self.parse_type() 
            
            if isinstance(base_type, ArrayType):
                # EAP specification usually prohibits array of arrays, enforce this for safety
                raise SyntaxError(f"Array of Array is not supported at line {self.current().line}")
                
            return ArrayType(type='ArrType', base_type=base_type, dimensions=dimensions)
            
        raise SyntaxError(f"Expected type at line {self.current().line}")

    def parse_parameter_list_block(self) -> List[Parameter]:
        """Parses a list of parameters inside the INPUT/OUTPUT block."""
        params = []
        # Checks for an IDENTIFIER to start a parameter definition
        while self.match(TokenType.IDENTIFIER): 
            names = [self.expect(TokenType.IDENTIFIER).value]
            while self.match(TokenType.COMMA):
                self.advance()
                names.append(self.expect(TokenType.IDENTIFIER).value)
            self.expect(TokenType.COLON)
            param_type = self.parse_type()
            self.expect(TokenType.SEMICOLON)
            
            for n in names:
                params.append(Parameter(type='Param', name=n, param_type=param_type))
        return params

    def parse_interface(self) -> List[Parameter]:
        """Parses the ΔΙΕΠΑΦΗ section for parameters."""
        # This will consume ΔΙΕΠΑΦΗ (INTERFACE)
        self.expect(TokenType.INTERFACE) 
        all_params = []
        
        # INPUT parameters (By Value)
        if self.match(TokenType.INPUT_PARAM):
            self.advance()
            all_params.extend(self.parse_parameter_list_block())

        # OUTPUT parameters (By Reference)
        if self.match(TokenType.OUTPUT_PARAM):
            self.advance()
            output_params = self.parse_parameter_list_block()
            for p in output_params:
                p.is_reference = True
            all_params.extend(output_params)
            final_output_params = []
            for p in output_params:
                # If we are parsing a Function, the output parameter with the 
                # same name as the function is the return value, not a call parameter.
                if function_name and p.name.upper() == function_name.upper():
                    # Skip the function's return variable
                    continue 
                
                # Otherwise, it's a true By Reference (OUTPUT) parameter
                p.is_reference = True
                final_output_params.append(p)
                
            all_params.extend(final_output_params)
            
        return all_params
    def parse_interface(self, function_name: Optional[str] = None) -> List[Parameter]:
        """Parses the ΔΙΕΠΑΦΗ section for parameters."""
        # This will consume ΔΙΕΠΑΦΗ (INTERFACE)
        self.expect(TokenType.INTERFACE) 
        all_params = []
        
        # INPUT parameters (By Value)
        if self.match(TokenType.INPUT_PARAM):
            self.advance()
            all_params.extend(self.parse_parameter_list_block())

       # OUTPUT parameters (By Reference)
        if self.match(TokenType.OUTPUT_PARAM):
            self.advance()
            output_params = self.parse_parameter_list_block()
            
            final_output_params = []
            for p in output_params:
                # CRITICAL FIX: Skip the function's return variable (same name as function)
                if function_name and p.name.upper() == function_name.upper():
                    continue
                
                # Check if this parameter already exists in INPUT (making it pass-by-reference)
                existing_param = None
                for existing in all_params:
                    if existing.name.upper() == p.name.upper():
                        existing_param = existing
                        break
                
                if existing_param:
                    # Parameter appears in both INPUT and OUTPUT - mark as reference
                    existing_param.is_reference = True
                else:
                    # Pure OUTPUT parameter (not in INPUT)
                    p.is_reference = True
                    final_output_params.append(p)
                
            all_params.extend(final_output_params)
            
        return all_params

    def parse_function(self) -> FunctionDeclaration:
        line = self.current().line
        self.expect(TokenType.FUNCTION)
        name = self.expect(TokenType.IDENTIFIER).value
        
        # Handle the simple parameter list in the header: factorial(n)
        if self.match(TokenType.LEFT_PAREN):
            self.advance()
            # Consume all identifiers/commas until the closing parenthesis.
            # We don't need to save them, as the formal interface follows.
            while not self.match(TokenType.RIGHT_PAREN):
                # Consume identifier or comma
                if not self.match(TokenType.IDENTIFIER, TokenType.COMMA):
                    # Raise an error if we find something unexpected inside the parens
                    raise SyntaxError(f"Expected parameter name or comma inside function header parentheses at line {self.current().line}")
                self.advance()
            self.expect(TokenType.RIGHT_PAREN) # Consume the closing ')'
        
        self.expect(TokenType.COLON) # Now the colon should follow
        
        return_type = self.parse_type()
       # Pass the function name (which is also the return variable)
        parameters = self.parse_interface(function_name=name)
        
        # Parse local DATA/VAR
        declarations = []
        if self.match(TokenType.DATA):
            self.advance()
            while self.match(TokenType.IDENTIFIER):
                names = [self.expect(TokenType.IDENTIFIER).value]
                while self.match(TokenType.COMMA):
                    self.advance()
                    names.append(self.expect(TokenType.IDENTIFIER).value)
                self.expect(TokenType.COLON)
                var_type = self.parse_type()
                self.expect(TokenType.SEMICOLON)
                for n in names:
                    declarations.append(VariableDeclaration(type='VarDecl', name=n, var_type=var_type, line=self.current().line))

        self.expect(TokenType.BEGIN)
        body = self.parse_block()
        self.expect(TokenType.END_FUNCTION)
        
        return FunctionDeclaration(type='FuncDecl', name=name, return_type=return_type, parameters=parameters, declarations=declarations, body=body, line=line)

    def parse_procedure(self) -> ProcedureDeclaration:
        line = self.current().line
        self.expect(TokenType.PROCEDURE)
        name = self.expect(TokenType.IDENTIFIER).value
        
        # FIX: Explicitly consume the simple parameter list in the header 
        if self.match(TokenType.LEFT_PAREN):
            self.advance()
            # Consume everything until the closing parenthesis
            while not self.match(TokenType.RIGHT_PAREN):
                if not self.match(TokenType.IDENTIFIER, TokenType.COMMA, TokenType.PERCENT):
                    raise SyntaxError(f"Expected parameter name, comma or % in procedure header at line {self.current().line}")
                self.advance()
            self.expect(TokenType.RIGHT_PAREN) # Consume the closing ')'
        
        # Parse the formal INTERFACE block
        parameters = self.parse_interface()
        
        # Parse local DATA/VAR
        declarations = []
        if self.match(TokenType.DATA):
            self.advance()
            while self.match(TokenType.IDENTIFIER):
                names = [self.expect(TokenType.IDENTIFIER).value]
                while self.match(TokenType.COMMA):
                    self.advance()
                    names.append(self.expect(TokenType.IDENTIFIER).value)
                self.expect(TokenType.COLON)
                var_type = self.parse_type()
                self.expect(TokenType.SEMICOLON)
                for n in names:
                    declarations.append(VariableDeclaration(type='VarDecl', name=n, var_type=var_type, line=self.current().line))
            
        self.expect(TokenType.BEGIN)
        body = self.parse_block()
        self.expect(TokenType.END_PROCEDURE)
        
        return ProcedureDeclaration(type='ProcDecl', name=name, parameters=parameters, declarations=declarations, body=body, line=line)


    def parse_block(self) -> List[ASTNode]:
        statements = []
        while not self.match(TokenType.END, TokenType.ELSE, TokenType.UNTIL, TokenType.END_IF, TokenType.END_FOR, TokenType.END_WHILE, TokenType.EOF, TokenType.END_FUNCTION, TokenType.END_PROCEDURE):
            statements.append(self.parse_statement())
        return statements
    
    def parse_statement(self) -> ASTNode:
        if self.match(TokenType.PRINT):
            return self.parse_print()
        elif self.match(TokenType.READ):
            return self.parse_read()
        elif self.match(TokenType.CALCULATE):  
            self.advance()                      
            return self.parse_call_statement()  
        elif self.match(TokenType.IF):
            return self.parse_if()
        elif self.match(TokenType.FOR):
            return self.parse_for()
        elif self.match(TokenType.WHILE):
            return self.parse_while()
        elif self.match(TokenType.REPEAT):
            return self.parse_repeat()
        elif self.match(TokenType.IDENTIFIER):
            # Check for function/procedure call statement
            if self.tokens[self.pos+1].type == TokenType.LEFT_PAREN:
                 # Check if the next non-parenthesis token is ASSIGN (e.g. F(x) := ...) which is not standard
                 # We assume F(x) is a call unless it is on the RHS of an assignment
                 # Since it's in statement position, it must be a procedure call or a function call used for its side effects (which is allowed).
                 return self.parse_call_statement()
            else:
                return self.parse_assignment()
        raise SyntaxError(f"Unexpected {self.current().type.name} at line {self.current().line}")

    def parse_call_statement(self) -> CallExpression:
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LEFT_PAREN)
        args = []
        if not self.match(TokenType.RIGHT_PAREN):
            # Skip % if present (pass-by-reference indicator)
            if self.match(TokenType.PERCENT):
                self.advance()
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                # Skip % if present
                if self.match(TokenType.PERCENT):
                    self.advance()
                args.append(self.parse_expression())

        self.expect(TokenType.RIGHT_PAREN)
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return CallExpression(type='Call', name=name, arguments=args, is_statement=True)
    
    def parse_print(self) -> PrintStatement:
        self.expect(TokenType.PRINT)
        self.expect(TokenType.LEFT_PAREN)
        exprs = []
        if not self.match(TokenType.RIGHT_PAREN):
            exprs.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                exprs.append(self.parse_expression())
        self.expect(TokenType.RIGHT_PAREN)
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return PrintStatement(type='Print', expressions=exprs)
    
    def parse_read(self) -> ReadStatement:
        self.expect(TokenType.READ)
        self.expect(TokenType.LEFT_PAREN)
        vars = []
        if not self.match(TokenType.RIGHT_PAREN):
            # Parse first variable (could be array access like PIN[i])
            var_expr = self.parse_primary()  # This handles both identifiers and array accesses
            vars.append(var_expr)
            while self.match(TokenType.COMMA):
                self.advance()
                var_expr = self.parse_primary()
                vars.append(var_expr)
        self.expect(TokenType.RIGHT_PAREN)
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return ReadStatement(type='Read', variables=vars)
    
    def parse_assignment(self) -> Assignment:
        name = self.expect(TokenType.IDENTIFIER).value
        indices = []
        if self.match(TokenType.LEFT_BRACKET):
            self.advance()
            indices.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                indices.append(self.parse_expression())
            self.expect(TokenType.RIGHT_BRACKET)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return Assignment(type='Assign', identifier=name, indices=indices, value=value)
    
    def parse_if(self) -> IfStatement:
        self.expect(TokenType.IF)
        cond = self.parse_expression()
        self.expect(TokenType.THEN)
        then_b = self.parse_block()
        else_b = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_b = self.parse_block()
        self.expect(TokenType.END_IF)
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return IfStatement(type='If', condition=cond, then_branch=then_b, else_branch=else_b)
    
    def parse_for(self) -> ForLoop:
        self.expect(TokenType.FOR)
        var = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        start = self.parse_expression()
        self.expect(TokenType.TO)
        end = self.parse_expression()
        step = Literal(type='Lit', value=1)
        if self.match(TokenType.STEP):
            self.advance()
            step = self.parse_expression()
        self.expect(TokenType.REPEAT)
        body = self.parse_block()
        self.expect(TokenType.END_FOR)
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return ForLoop(type='For', variable=var, start=start, end=end, step=step, body=body)
    
    def parse_while(self) -> WhileLoop:
        self.expect(TokenType.WHILE)
        cond = self.parse_expression()
        self.expect(TokenType.REPEAT)
        body = self.parse_block()
        self.expect(TokenType.END_WHILE)
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return WhileLoop(type='While', condition=cond, body=body)
    
    def parse_repeat(self) -> WhileLoop:
        self.expect(TokenType.REPEAT)
        body = self.parse_block()
        self.expect(TokenType.UNTIL)
        cond = self.parse_expression()
        if self.match(TokenType.SEMICOLON):
            self.advance()
        not_cond = UnaryOp(type='Unary', operator='NOT', operand=cond)
        return WhileLoop(type='RepeatUntil', condition=not_cond, body=body)
    
    def parse_expression(self) -> ASTNode:
        return self.parse_or()
    
    def parse_or(self) -> ASTNode:
        left = self.parse_and()
        while self.match(TokenType.OR):
            op = self.current().value
            self.advance()
            right = self.parse_and()
            left = BinaryOp(type='BinOp', operator=op, left=left, right=right)
        return left
    
    def parse_and(self) -> ASTNode:
        left = self.parse_comparison()
        while self.match(TokenType.AND):
            op = self.current().value
            self.advance()
            right = self.parse_comparison()
            left = BinaryOp(type='BinOp', operator=op, left=left, right=right)
        return left
    
    def parse_comparison(self) -> ASTNode:
        left = self.parse_additive()
        while self.match(TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LESS_THAN, TokenType.GREATER_THAN, TokenType.LESS_EQUALS, TokenType.GREATER_EQUALS):
            op = self.current().value
            self.advance()
            right = self.parse_additive()
            left = BinaryOp(type='BinOp', operator=op, left=left, right=right)
        return left
    
    def parse_additive(self) -> ASTNode:
        left = self.parse_multiplicative()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.current().value
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(type='BinOp', operator=op, left=left, right=right)
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        left = self.parse_unary()
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MOD, TokenType.DIV):
            op = self.current().value
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(type='BinOp', operator=op, left=left, right=right)
        return left
    
    def parse_unary(self) -> ASTNode:
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.current().value
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(type='Unary', operator=op, operand=operand)
        return self.parse_primary()
    
    def parse_primary(self) -> ASTNode:
        if self.match(TokenType.NUMBER):
            val = self.current().value
            self.advance()
            return Literal(type='Lit', value=val)
        
        # New: Handle Boolean Literal
        if self.match(TokenType.BOOLEAN_LITERAL):
            val_str = self.current().value.upper()
            self.advance()
            val = True if val_str in ('ΑΛΗΘΗΣ', 'TRUE') else False
            return Literal(type='Lit', value=val)
        
        if self.match(TokenType.STRING):
            val = self.current().value
            self.advance()
            return Literal(type='Lit', value=val)
        
        if self.match(TokenType.IDENTIFIER):
            name = self.current().value
            
            # Look ahead for a function/procedure call
            if self.tokens[self.pos+1].type == TokenType.LEFT_PAREN:
                self.advance()
                self.expect(TokenType.LEFT_PAREN)
                args = []
                if not self.match(TokenType.RIGHT_PAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        args.append(self.parse_expression())
                self.expect(TokenType.RIGHT_PAREN)
                return CallExpression(type='Call', name=name, arguments=args, is_statement=False)
            
            self.advance()
            if self.match(TokenType.LEFT_BRACKET):
                self.advance()
                indices = [self.parse_expression()]
                while self.match(TokenType.COMMA):
                    self.advance()
                    indices.append(self.parse_expression())
                self.expect(TokenType.RIGHT_BRACKET)
                return ArrayAccess(type='ArrAcc', name=name, indices=indices)
            return Identifier(type='Id', name=name)
        
        if self.match(TokenType.LEFT_PAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RIGHT_PAREN)
            return expr
        
        raise SyntaxError(f"Unexpected {self.current().type.name} at line {self.current().line}")


# =============================================================================
# INTERPRETER
# =============================================================================

class ArrayObject:
    """Represents a dynamically sized EAP array with bounds checking."""
    def __init__(self, bounds: List[Dict[str, int]]):
        self.data = {}
        self.bounds = bounds
    
    def _validate_indices(self, indices: List[int]):
        if len(indices) != len(self.bounds):
            raise RuntimeError(f"Incorrect number of indices ({len(indices)}). Expected {len(self.bounds)}.")

        for i, index in enumerate(indices):
            bound = self.bounds[i]
            if not isinstance(index, int) or index < bound['from'] or index > bound['to']:
                raise RuntimeError(f"Array index {index} is out of bounds for dimension {i+1}. Expected range: [{bound['from']}..{bound['to']}].")

    def get(self, indices: List[int]):
        self._validate_indices(indices)
        key = ','.join(str(i) for i in indices)
        return self.data.get(key, 0)
    
    def set(self, indices: List[int], value: Any):
        self._validate_indices(indices)
        key = ','.join(str(i) for i in indices)
        self.data[key] = value


class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent
        self.subroutines = {}
    
    def define(self, name, value):
        self.values[name.upper()] = value
    
    def define_subroutine(self, name, declaration):
        self.subroutines[name.upper()] = declaration
    
    def get(self, name):
        key = name.upper()
        if key in self.values:
            return self.values[key]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: {name}")

    def get_subroutine(self, name):
        key = name.upper()
        if key in self.subroutines:
            return self.subroutines[key]
        if self.parent:
            return self.parent.get_subroutine(name)
        raise RuntimeError(f"Undefined function or procedure: {name}")
    
    def assign(self, name, value):
        key = name.upper()
        if key in self.values:
            self.values[key] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        self.values[key] = value 


class Interpreter:
    
    def __init__(self, debug=False):
        self.env = Environment()
        self.debug = debug
        # Define the EOLN constant for EAP compatibility
        self.env.define("EOLN", "__EOLN__") # Use a sentinel value
 
    def log(self, msg):
        if self.debug:
            print(f"[DEBUG] {msg}", file=sys.stderr)
    
    def execute(self, program: Program):
        self.log(f"Executing program: {program.name}")
        
        # --- Phase 1: Define Constants and Subroutines ---
        for decl in program.declarations:
            if isinstance(decl, ConstantDeclaration):
                value = self.evaluate(decl.value)
                self.env.define(decl.name, value)
                self.log(f"Defined constant: {decl.name} = {value}")
            
            elif isinstance(decl, (FunctionDeclaration, ProcedureDeclaration)):
                self.env.define_subroutine(decl.name, decl)
                self.log(f"Defined subroutine: {decl.name}")
        
        # --- Phase 2: Define Variables (including arrays, which now rely on constants) ---
        for decl in program.declarations:
            if isinstance(decl, VariableDeclaration):
                if isinstance(decl.var_type, ArrayType):
                    evaluated_bounds = []
                    for dim in decl.var_type.dimensions:
                        # Array bounds must be evaluated first (they rely only on constants/literals)
                        try:
                            start = int(self.evaluate(dim.start))
                            end = int(self.evaluate(dim.end))
                        except Exception as e:
                            line = decl.line if decl.line != 0 else '?'
                            raise RuntimeError(f"Array bounds must evaluate to integers. Error in '{decl.name}' array declaration (line {line}): {e}")

                        if not isinstance(start, int) or not isinstance(end, int):
                             raise RuntimeError("Array bounds must evaluate to integers.")
                        
                        evaluated_bounds.append({'from': start, 'to': end})
                        
                    self.env.define(decl.name, ArrayObject(evaluated_bounds))
                    self.log(f"Declared array: {decl.name} with bounds: {evaluated_bounds}")
                else:
                    self.env.define(decl.name, 0)
                self.log(f"Declared variable: {decl.name}")
            
        
        # Execute main body
        for stmt in program.body:
            self.execute_statement(stmt)

    def _execute_subroutine(self, subroutine_decl: Union[FunctionDeclaration, ProcedureDeclaration], call: CallExpression):
        if len(call.arguments) != len(subroutine_decl.parameters):
            raise RuntimeError(f"Function/Procedure '{call.name}' called with {len(call.arguments)} arguments, expected {len(subroutine_decl.parameters)}.")

        local_env = Environment(parent=self.env)
        
        # 1. Handle Parameter Passing (By Value / By Reference)
        for param, arg_expr in zip(subroutine_decl.parameters, call.arguments):
            
            if param.is_reference:
                # Parameter is passed By Reference (OUTPUT)
                if not isinstance(arg_expr, Identifier) and not isinstance(arg_expr, ArrayAccess):
                    raise RuntimeError(f"Argument for reference parameter '{param.name}' must be a variable or array access passed by name.")

                # For simple types, we rely on the parent environment's assign method for assignment.
                # For array objects, we pass the ArrayObject reference.
                arg_name = arg_expr.name.upper()
                
                try:
                    arg_val = self.env.get(arg_expr.name)
                    local_env.define(param.name, arg_val) # Define locally, will be updated in parent on assignment
                except RuntimeError:
                     raise RuntimeError(f"Reference parameter '{param.name}' argument '{arg_expr.name}' not found in caller's environment.")

            else:
                # Parameter is passed By Value (INPUT)
                value = self.evaluate(arg_expr)
                local_env.define(param.name, value)
        
        # 2. Process Local Declarations
        for decl in subroutine_decl.declarations:
            if isinstance(decl, VariableDeclaration):
                if isinstance(decl.var_type, ArrayType):
                    evaluated_bounds = []
                    for dim in decl.var_type.dimensions:
                        # Array bounds must be evaluated first (they rely only on constants/literals)
                        try:
                            # Evaluate bounds in the current (caller's) environment, which should contain all global constants.
                            start = int(self.evaluate(dim.start))
                            end = int(self.evaluate(dim.end))
                        except Exception as e:
                            line = decl.line if decl.line != 0 else '?'
                            raise RuntimeError(f"Array bounds must evaluate to integers. Error in '{decl.name}' array declaration (line {line}): {e}")

                        if not isinstance(start, int) or not isinstance(end, int):
                             raise RuntimeError("Array bounds must evaluate to integers.")
                        
                        evaluated_bounds.append({'from': start, 'to': end})
                        
                    local_env.define(decl.name, ArrayObject(evaluated_bounds))
                    self.log(f"Declared local array: {decl.name} with bounds: {evaluated_bounds}")
                else:
                    # Simple variables are initialized to 0/empty
                    local_env.define(decl.name, 0)
                    self.log(f"Declared local variable: {decl.name}")
                
        # 3. Execute Subroutine Body
        # Temporarily switch the interpreter's environment
        old_env = self.env
        self.env = local_env
        return_value = None
        try:
            for stmt in subroutine_decl.body:
                self.execute_statement(stmt)
        finally:
            self.env = old_env

        # 4. Handle Return Value (if function)
        if isinstance(subroutine_decl, FunctionDeclaration):
            # The return value is stored in a local variable named after the function
            return_value = local_env.get(subroutine_decl.name)
        
        # Procedures return nothing
        return return_value


    def execute_statement(self, stmt: ASTNode):
        if isinstance(stmt, Assignment):
            value = self.evaluate(stmt.value)
            if stmt.indices:
                arr = self.env.get(stmt.identifier)
                if not isinstance(arr, ArrayObject):
                    raise RuntimeError(f"{stmt.identifier} is not an array")
                indices = [int(self.evaluate(idx)) for idx in stmt.indices]
                arr.set(indices, value)
                self.log(f"Array assign: {stmt.identifier}[{indices}] = {value}")
            else:
                self.env.assign(stmt.identifier, value)
                self.log(f"Assign: {stmt.identifier} = {value}")
        
 #       elif isinstance(stmt, PrintStatement):
 #           parts = []
 #           has_eoln = False
 #           for expr in stmt.expressions:
 #               value = self.evaluate(expr)
 #               if value == "__EOLN__": # Check for the EOLN sentinel
 #                   has_eoln = True
 #               else:
 #                   parts.append(str(value))
 #           
 #           # Print the collected parts separated by a space
 #           print(' '.join(parts), end='\n' if has_eoln else '')
 #       
        elif isinstance(stmt, PrintStatement):
            # Process each expression in order, printing EOLN immediately when encountered
            for i, expr in enumerate(stmt.expressions):
                value = self.evaluate(expr)
                if value == "__EOLN__":
                    # Print newline immediately
                    print()
                else:
                    # Print the value
                    # Add space before if not the first item and previous wasn't EOLN
                    if i > 0 and stmt.expressions[i-1] and self.evaluate(stmt.expressions[i-1]) != "__EOLN__":
                        print(' ', end='')
                    print(str(value), end='')
                    
        elif isinstance(stmt, ReadStatement):
            for var_expr in stmt.variables:
                # Determine variable name for prompt
                if isinstance(var_expr, Identifier):
                    var_name = var_expr.name
                elif isinstance(var_expr, ArrayAccess):
                    indices = [int(self.evaluate(idx)) for idx in var_expr.indices]
                    var_name = f"{var_expr.name}[{','.join(map(str, indices))}]"
                else:
                    var_name = "variable"
                
                try:
                    raw_input = input(f"Enter value for {var_name}: ")
                    
                    # 2. Ελέγχουμε αν η είσοδος είναι κενή/ελλιπής
                    if not raw_input.strip():
                        # Αν είναι κενή, αναθέτουμε μια τιμή (-1) που θα αποτύχει σίγουρα 
                        # στον έλεγχο αμυντικού προγραμματισμού (π.χ. < 100), αναγκάζοντας
                        # τον βρόχο REPEAT-UNTIL να επαναλάβει το ΔΙΑΒΑΣΕ.
                        value = -1 
                    else:
                        try:
                            # 3. Προσπαθούμε να μετατρέψουμε σε αριθμό (για INTEGER/REAL)
                            if '.' in raw_input:
                                value = float(raw_input)
                            else:
                                value = int(raw_input)
                        except ValueError:
                            # 4. Αν αποτύχει η μετατροπή (π.χ. εισήχθη συμβολοσειρά), 
                            # αναθέτουμε τη συμβολοσειρά.
                            value = raw_input
                            
                  # Assign to the variable or array element
                    if isinstance(var_expr, Identifier):
                        self.env.assign(var_expr.name, value)
                        self.log(f"Read: {var_expr.name} = {value}")
                    elif isinstance(var_expr, ArrayAccess):
                        arr = self.env.get(var_expr.name)
                        if not isinstance(arr, ArrayObject):
                            raise RuntimeError(f"{var_expr.name} is not an array")
                        indices = [int(self.evaluate(idx)) for idx in var_expr.indices]
                        arr.set(indices, value)
                        self.log(f"Read: {var_expr.name}[{indices}] = {value}")
                except EOFError:
                    # Handle EOF
                    if isinstance(var_expr, Identifier):
                        self.env.assign(var_expr.name, -1)
                        self.log(f"Read: {var_expr.name} = -1 (EOF)")
                    elif isinstance(var_expr, ArrayAccess):
                        arr = self.env.get(var_expr.name)
                        indices = [int(self.evaluate(idx)) for idx in var_expr.indices]
                        arr.set(indices, -1)
                        self.log(f"Read: {var_expr.name}[{indices}] = -1 (EOF)")

        elif isinstance(stmt, IfStatement):
            if self.to_bool(self.evaluate(stmt.condition)):
                for s in stmt.then_branch:
                    self.execute_statement(s)
            elif stmt.else_branch:
                for s in stmt.else_branch:
                    self.execute_statement(s)
        
        elif isinstance(stmt, ForLoop):
            # For loop variables should be local to the loop body in modern EAP, 
            # but we use the simpler common implementation for now.
            start = int(self.evaluate(stmt.start))
            end = int(self.evaluate(stmt.end))
            step = int(self.evaluate(stmt.step))
            
            current = start

            if step > 0:
                while current <= end:
                    self.env.assign(stmt.variable, current) 
                    for s in stmt.body:
                        self.execute_statement(s)
                    current += step
            else:
                while current >= end:
                    self.env.assign(stmt.variable, current)
                    for s in stmt.body:
                        self.execute_statement(s)
                    current += step

        elif isinstance(stmt, WhileLoop):
            while self.to_bool(self.evaluate(stmt.condition)):
                for s in stmt.body:
                    self.execute_statement(s)
        
        elif isinstance(stmt, CallExpression) and stmt.is_statement:
            subroutine_decl = self.env.get_subroutine(stmt.name)
            self._execute_subroutine(subroutine_decl, stmt)

        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt).__name__}")

    def evaluate(self, expr: ASTNode) -> Any:
        if isinstance(expr, Literal):
            return expr.value

        elif isinstance(expr, Identifier):
            value = self.env.get(expr.name)
            if isinstance(value, ArrayObject):
                return value
            return value

        elif isinstance(expr, BinaryOp):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            op = expr.operator

            if op == '+': return left + right
            elif op == '-': return left - right
            elif op == '*': return left * right
            elif op == '/': 
                if right == 0: raise RuntimeError("Division by zero")
                return left / right
            elif op == 'DIV': 
                if right == 0: raise RuntimeError("Division by zero")
                return int(left / right)
            elif op in ('MOD', '%'): 
                if right == 0: raise RuntimeError("Modulo by zero")
                return left % right 
            
            elif op == '=': return left == right
            elif op == '<>': return left != right
            elif op == '<': return left < right
            elif op == '>': return left > right
            elif op == '<=': return left <= right
            elif op == '>=': return left >= right
            
            elif op in ('AND', 'ΚΑΙ'): return self.to_bool(left) and self.to_bool(right)
            elif op in ('OR', 'Ή'): return self.to_bool(left) or self.to_bool(right)
            
            else: raise RuntimeError(f"Unknown operator: {op}")

        elif isinstance(expr, UnaryOp):
            operand = self.evaluate(expr.operand)
            if expr.operator == '-': return -operand
            elif expr.operator in ('NOT', 'ΟΧΙ'): return not self.to_bool(operand)
            else: raise RuntimeError(f"Unknown unary operator: {expr.operator}")

        elif isinstance(expr, ArrayAccess):
            arr = self.env.get(expr.name)
            if not isinstance(arr, ArrayObject):
                raise RuntimeError(f"{expr.name} is not an array")
            indices = [int(self.evaluate(idx)) for idx in expr.indices]
            return arr.get(indices)

        elif isinstance(expr, CallExpression) and not expr.is_statement:
            subroutine_decl = self.env.get_subroutine(expr.name)
            if not isinstance(subroutine_decl, FunctionDeclaration):
                 raise RuntimeError(f"Procedure '{expr.name}' used as an expression (function).")
            return self._execute_subroutine(subroutine_decl, expr)

        else:
            raise RuntimeError(f"Cannot evaluate: {type(expr).__name__}")

    def to_bool(self, value: Any) -> bool:
        if isinstance(value, bool): return value
        # Treat non-zero number, non-empty string, or truthy object as True
        if isinstance(value, (int, float)): return value != 0
        if isinstance(value, str): return len(value) > 0
        return bool(value)


def detect_encoding(filename):
    """Detect file encoding (UTF-8 or Windows-1253)"""
    try:
        with open(filename, 'rb') as f:
            raw = f.read()
            # Try UTF-8 first
            try:
                text = raw.decode('utf-8')
                if 'ΑΛΓΟΡΙΘΜΟΣ' in text.upper() or 'ALGORITHM' in text.upper():
                    return text, 'utf-8'
            except:
                pass
            
            # Try Windows-1253 (often used for Greek text)
            try:
                text = raw.decode('windows-1253')
                if 'ΑΛΓΟΡΙΘΜΟΣ' in text.upper() or 'ALGORITHM' in text.upper():
                    return text, 'windows-1253'
            except:
                pass
            
            # Default to UTF-8 with replacement for corrupted bytes
            return raw.decode('utf-8', errors='replace'), 'utf-8'

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("EAP Pseudocode Interpreter")
        print(f"Usage: {sys.argv[0]} <file.eap> [--debug]")
        print("\nExample:")
        print(f"  {sys.argv[0]} program.eap")
        print(f"  {sys.argv[0]} program.eap --debug")
        sys.exit(1)
    filename = sys.argv[1]
    debug = '--debug' in sys.argv

    # Read file
    code, encoding = detect_encoding(filename)

    if debug:
        print(f"[DEBUG] File encoding: {encoding}", file=sys.stderr)
        print(f"[DEBUG] File size: {len(code)} characters", file=sys.stderr)

    try:
        # Tokenize
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        if debug:
            print(f"[DEBUG] Generated {len(tokens)} tokens", file=sys.stderr)
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        if debug:
            print(f"[DEBUG] Parsed program: {ast.name}", file=sys.stderr)
            print(f"[DEBUG] Declarations: {len(ast.declarations)}", file=sys.stderr)
            print(f"[DEBUG] Statements: {len(ast.body)}", file=sys.stderr)
        
        # Execute
        interpreter = Interpreter(debug=debug)
        interpreter.execute(ast)
        
    except SyntaxError as e:
        print(f"Syntax Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nExecution interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
