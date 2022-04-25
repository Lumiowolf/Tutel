# Projekt wstępny

## 1. Opis funkcjonalny

Język w założeniu jest oparty na LOGO, języku do nauki programowania, w którym sterujemy żółwiem zostawiającym graficzny
ślad swojej ścieżki.
Mój język składniowo będzie oparty na aktualnie popularnych językach programowania Python i JavaScript.
Oprócz przyjemniejszej składni usprawnieniem względem LOGO będzie możliwość tworzenia wielu żółwi w jednym programie, o
dowolnym kolorze oraz położeniu początkowym.
Docelowo język będzie zintegrowany z graficznym interfejsem.

Język będzie obsługiwał:

* instrukcję warunkową if - {elif} - [else]
* pętlę for oraz while
* operatory matematyczne: +, -, *, /, %, (), // (dzielenie całkowite)
* operatory logiczne: and, or, not, in, ==, !=, >, >=, <, <=, ()
* operatory przypisania: =, +=, -=, *=, /=, %=
* tworzenie własnych funkcji i wywoływanie (w tym rekurencyjne)
* typy danych: turtle, color, position, orientation, int, string, boolean, null
* wypisywanie danych na standardowe wyjście
* wprowadzanie danych przez standardowe wejście
* operacje na żółwiach: idź do przodu, idź do tyłu, obróć się w prawo/lewo o podaną liczbę stopni (domyślnie 90), zmiana
  koloru i położenia
* tworzenie list, dodawanie/usuwanie/odczytywanie elementów listy

## 2. Przykłady użycia

| Kod                                                                                                                                                                                                                                                                                                         | Działanie                                                                                                                                    |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `name_1 = turtle()`                                                                                                                                                                                                                                                                                         | Utworzenie żółwia z podstawowymi parametrami                                                                                                 |
| `name_2 = turtle(color='red')`                                                                                                                                                                                                                                                                              | Utworzenie czerwonego żółwia                                                                                                                 |
| `name_3 = turtle(color=color(0, 0, 255))`                                                                                                                                                                                                                                                                   | Utworzenie niebieskiego żółwia (RGB)                                                                                                         |
| `name_4 = turtle(position=(15, 20))`                                                                                                                                                                                                                                                                        | Utworzenie żółwia na zadanej pozycji                                                                                                         |
| `name_1.color = black`<br>`name_1.color = color(100, 200, 50)`<br>`name_1.position.x = 20`<br>`name_1.position.y = -10`<br>`name_1.orientation = right`<br>`name_1.orientation = 90`                                                                                                                        | Zmiana parametrów żółwia                                                                                                                     |
| `name_1.forward(10)`                                                                                                                                                                                                                                                                                        | Żółw 'name_1' idzie o 10 kroków naprzód                                                                                                      |
| `name_1.backward(20)`                                                                                                                                                                                                                                                                                       | Żółw 'name_1' idzie o 20 kroków do tyłu                                                                                                      |
| `name_1.turn_right()`<br>`name_1.turn_left(15)`                                                                                                                                                                                                                                                             | Żółw 'name_1' skręca w prawo/lewo o $90^o$ (względem aktualnej orientacji)                                                                   |
| `a = null`<br>`b = 10`<br>`c = "c"`<br>`d = "text"`<br>`f = true`<br>`g = false`                                                                                                                                                                                                                            | Tworzenie zmiennych<br>Domyślna wartość: null<br>Dopuszczalne typy danych: null, integer, real number, character, string, boolean            |
| `if(name_1.position.x > 50)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name_1.turn_right()`<br>`elif(name_1.position.y < -15)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name_1.turn_left()`<br>`elif(name_2.position.y >= 10)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name_1.turn_right(20)`<br>`else`<br>&nbsp;&nbsp;&nbsp;&nbsp;`print("else")` | Złożony warunek                                                                                                                              |
| `if(name_1.color == red and f or not g) {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name_1.forward(2)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name_2.backward(4)`<br>`}`                                                                                                                                                            | Warunek z blokiem w klamrach                                                                                                                 |
| `exampleList = [1, 2, 3, 'a', "text"]`<br>`exampleList.add(2)`<br>`exampleList.add("b")`<br>`exampleList.remove(0)`<br>`print(exampleList[2])`                                                                                                                                                              | Utworzenie listy, dodanie elementu do listy (na koniec), usunięcie elementu spod podanego indeksu, odczytanie elementu spod podanego indeksu |
| `for(element in list) {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`print(element)`<br>`}`                                                                                                                                                                                                                                 | Wypisz każdy element z listy                                                                                                                 |
| `foo(param1, param2): {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`i = 10`<br>&nbsp;&nbsp;&nbsp;&nbsp;`return i + param1 * param2`<br>`}`<br>`bar(): {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`print(foo(50, 20))`<br>`}`<br>                                                                                                        | Definicja i wywołanie funkcji 'foo'                                                                                                          |
| `fun(): print("debug")`                                                                                                                                                                                                                                                                                     | Jednoliniowa funkcja nie wymaga klamer                                                                                                       |

## 3. Opis gramatyki

### 3.1. Konwecje leksykalne

```
literal      = string | number | "true" | "false" | "null";
string       = """, {char | escaping}, """ | "'", {char | escaping}, "'";
number       = digit | nonZeroDigit, {digit};
digit        = "0" | nonZeroDigit;
nonZeroDigit = "1" | ... | "9";
identifier   = letter, {letter | digit | "_"} | "_", {letter | digit | "_"};
comment      = "#", {char};
escaping     = "\", specialChar;
```

### 3.2. Gramatyka

```
program             = {functionDef};

functionDef         = identifier, "(", paramList, ")", ":", block;
paramList           = [identifier, {",", identifier}];

block               = "{", {statement}, "}";
statement           = simpleStatement, ";"
                    | compoundStatement;
simpleStatement     = assignment
                    | expression
                    | returnStatement;
compoundStatement   = ifStatement
                    | forStatement;

assignment          = identifier, assignmentOperator, expression;
assignmentOperator  = "="
                    | "+="
                    | "-="
                    | "*="
                    | "/="
                    | "%=";

returnStatement     = "return"
                    | "return", expression, {",", expression};

ifStatement         = "if", "(", expression, ")", (statement | block),
                      {elifBlock}, [elseBlock];
elifBlock           = "elif", "(", expression, ")", (statement | block);
elseBlock           = "else", (statement | block);

forStatement        = "for", "(", identifier, "in", expression, ")",
                      (statement | block);

expression          = disjunction;
disjunction         = conjunction, {"or", conjunction}
                    | conjunction;
conjunction         = inversion, {"and", inversion}
                    | inversion;
inversion           = "not", inversion
                    | comparison;
comparison          = compare_op_sum, {compare_op_sum};
compare_op_sum      = eq_sum;
                    | noteq_sum;
                    | lte_sum;
                    | lt_sum;
                    | gte_sum;
                    | gt_sum;
                    | notin_sum;
                    | in_sum;
eq_sum              = "==", sum;
noteq_sum           = "!=", sum;
lte_sum             = "<=", sum;
lt_sum              = "<", sum;
gte_sum             = ">=", sum;
gt_sum              = ">", sum;
notin_sum           = "not", "in", sum;
in_sum              = "in", sum;
sum                 = sum, "+", term
                    | sum, "-", term
                    | term;
term                = term, "*", factor
                    | term, "/", factor
                    | term, "//", factor
                    | term, "%", factor
                    | factor;
factor              = "+" factor
                    | "-" factor
                    | primary;
primary             = primary, ".", identifier
                    | primary, "(", [arguments], ")"
                    | primary, "[", number, "]"
                    | atom;
arguments           = [expression, {",", expression}];
atom                = identifier
                    | literal
                    | list
                    | listAccess;

list                = "[", [expression, {",", expression}], "]";
listAccess          = identifier, "[", number, "]"
```

## 4. Opis techniczny

### 4.1. Wymagania funkcjonalne

* Interpreter będzie się składał z analizatora leksykalnego i parsera.
* Lekser będzie odczytywał dane wejściowe (kod użytkownika) ze strumienia wejściowego (io.StringIO), a parser będzie
  pobierał kolejne tokeny poprzez wywołanie odpowiedniej metody leksera (get_next_token()).
* Zadaniem leksera będzie wydobywanie z kodu kolejnych tekenów.
* Zadaniem parsera będzie pobieranie od leksera tokenów i składanie z nich kodu według gramatyki.
* Pobrane identyfikatory funkcji i zmiennych będą przechowywane w słowniku. Dzięki temu będzie można kontrolować
  niepowtarzalność.
* Program będzie uruchamiany przez interpreter Pythona w konsoli, czyli np. `python3 tutel.py`.
* Konsola pozostanie otwarta jedynie do wyświetlania wartości podanej do funkcji `print` oraz wczytywania danych od
  użytkownika przez funkcję `input`.
* Obiekty i zmienne będą przekazywane do funkcji jako referencja.
* Niedopuszczalne będzie tworzenie identyfikatorów o takiej samej nazwie jak słowo kluczowe języka lub istniejący już
  identyfikator, przy czym najwyższy priorytet mają słowa kluczowe, a następnie nazwy funkcji. To znaczy, że zmienna nie
  może mieć takiej samej nazwy jak istniejąca funkcja. Duplikacja identyfikatorów będzie traktowana jako błąd już na
  etapie interpretacji.
* Po uruchomieniu programu zostanie wyświetlony interfejs graficzny z podziałem na część do pisania kodu (prosty, ale
  przyjemny edytor) oraz na część wyświetlającą wykonanie skryptu.
* Będzie możliwość ukrycia jednej z tych części i wyświetlenie drugiej w pełnym oknie.
* Użytkownik będzie mógł utworzyć nowy skrypt, otworzyć skrypt z pliku na dysku i zapisać do pliku.
* Interfejs będzie miał listę rozwijaną do wyboru funkcji, od której rozpocznie się wykonanie programu.
* Obsługa błędów:
    * Błędy leksera: program nie zostanie wykonany, na standardowe wyjście zostaną wypisane napotkane błędy leksykalne
      wraz z położeniem w pliku.
    * Błędy prasera: program nie zostanie wykonany, na standardowe wyjście zostaną wypisany pierwszy napotkany błąd
      gramatyczny wraz z położeniem w pliku.
    * Błędy wykonania: program przerwie wykonanie w momencie napotkania błędu i wypisze typ błędu oraz stacktrace na
      standardowe wyjście.

### 4.2. Wymagania niefunkcjonalne

* Interpreter będzie napisany w języku Python v3.10.
* Do interfejsu graficznego wykorzystam bibliotekę PyQt5 w aktualnie najnowszej wersji.
* Docelowo aplikacja będzie mogła być uruchomiona na każdym systemie wspierającym Pythona w wybranej wersji i PyQt5.
  Minimum to Windows 10 i Ubuntu 20.04.

### 4.3. Rozpoznawane tokeny

```
T_IF:                   "if"
T_ELIF:                 "elif
T_ELSE:                 "else
T_FOR:                  "for"
T_WHILE:                "while"
T_RETURN:               "return"
T_PLUS:                 "+"
T_MINUS:                "-"
T_MULTIPLY:             "*"
T_DIVIDE:               "/"
T_INT_DIVIDE:           "//"
T_MODULUS:              "%"
T_AND:                  "and"
T_OR:                   "or"
T_IN:                   "in"
T_NOT:                  "not"
T_LESS_THAN:            "<"
T_LESS_EQUAL_THAN:      "<="
T_GREATER_THAN:         ">"
T_GREATER_EQUAL_THAN:   ">="
T_EQUAL:                "=="
T_NOTEQUAL:             "!="
T_ASSIGNMENT:           "="
T_PLUS_ASSIGNMENT:      "+="
T_MINUS_ASSIGNMENT:     "-="
T_MULTIPLY_ASSIGNMENT:  "*="
T_DIVIDE_ASSIGNMENT:    "/="
T_MODULUS_ASSIGNMENT:   "%="
T_TRUE:                 "true"
T_FALSE:                "false"
T_NULL:                 "null"
T_QUOTE:                "'"
T_DOUBLE_QUOTE:         '"'
T_COMMENT:              "#"
T_COLON:                ":"
T_SEMICOLON:            ";"
T_ESCAPE:               "\"
T_LEFT_BRACKET:         "("
T_RIGHT_BRACKET:        ")"
T_LEFT_SQUARE_BRACKET:  "["
T_RIGHT_SQUARE_BRACKET: "]"
T_LEFT_CURLY_BRACKET:   "{"
T_RIGHT_CURLY_BRACKET:  "}"
T_DOT:                  "."
T_COMMA:                ","
T_ETX:                  "\x03"

T_IDENTIFIER: identyfikator
T_TEXT_CONST: stała tekstowa
T_NUMBER:     liczba
T_ILLEGAL:    symbol niedozwolony w danym miejscu
T_UNKNOWN:    symbol nieznany
```

## 5. Opis testowania

### 5.1. Testowanie leksera

* Testy jednostkowe sprawdzające wykrycie w prostych sekwencjach:
    * ETX,
    * komentarza,
    * identyfikatorów,
    * słów kluczowych,
    * stałej tekstowej,
    * liczby,
    * operatorów,
    * znaków interpunkcyjnych.
* Testy jednostkowe sprawdzające rozpoznanie różnych tokenów bardziej skomplikowanych sekwencjach:
    * jednoliniowych,
    * wieloliniowych.
* Testy jednostkowe sprawdzające kontrolę błędów, czyli wykrycie tokenów:
    * T_UNKNOWN - nierozpoznany symbol,
    * T_ILLEGAL - symbol niedozwolony (przerwanie stałej tekstowej znakiem nowej linii lub ETX, przekroczenie maksymalnej długości identyfikatora).

### 5.2. Testowanie parsera

Testy jednostkowe sprawdzające parsowanie przykładów wszystkich struktur, włączając w to przypadki rzadkie.

### 5.3. Testowanie finalnej aplikacji z GUI

Testy manualne polegające na sprawdzeniu wyniku przygotowanych skryptów.