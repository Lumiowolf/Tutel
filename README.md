# Projekt TKOM - interpreter języka Tutel

## 1. Opis funkcjonalny

Język w założeniu jest oparty na LOGO, języku do nauki programowania, w którym sterujemy żółwiem zostawiającym graficzny
ślad swojej ścieżki.
Mój język składniowo jest oparty na aktualnie popularnych językach programowania Python i JavaScript.
Oprócz przyjemniejszej składni (względem LOGO) usprawnieniem będzie możliwość tworzenia wielu żółwi w jednym programie, o
różnych kolorach, położeniu i kącie obrotu.
Język jest zintegrowany z graficznym interfejsem, który wyświetla efekty działania skryptów.

Język obsługuje:

* instrukcję warunkową if - {elif} - [else]
* pętlę for oraz while
* operatory matematyczne: +, -, *, /, %, (), // (dzielenie całkowite)
* operatory logiczne: and, or, not, in, ==, !=, >, >=, <, <=, ()
* operatory przypisania: =, +=, -=, *=, /=, %=
* tworzenie własnych funkcji i wywoływanie (w tym rekurencyjne)
* typy danych: Turtle, Color (enum), Position, Orientation, int, string, boolean, null
* wypisywanie danych na standardowe wyjście
* wprowadzanie danych przez standardowe wejście
* operacje na żółwiach: idź do przodu, obróć się w prawo/lewo o $90^o$ lub inną podaną, zmiana koloru, położenia i kąta
  obrotu
* tworzenie list, dodawanie/odczytywanie elementów listy

## 2. Przykłady użycia

| Kod                                                                                                                                                                                                                                                                                                                                        | Działanie                                                                                                                         |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `name_1 = Turtle();`                                                                                                                                                                                                                                                                                                                       | Utworzenie żółwia z podstawowymi parametrami                                                                                      |
| `name_1.setColor(Color.Black);`                                                                                                                                                                                                                                                                                                            | Zmiana koloru                                                                                                                     |
| `name_1.setPosition(100, 200);`                                                                                                                                                                                                                                                                                                            | Zmiana pozycji                                                                                                                    |
| `name_1.setOrientation(45);`                                                                                                                                                                                                                                                                                                               | Zmiana orientacji                                                                                                                 |
| `name_1.forward(10);`                                                                                                                                                                                                                                                                                                                      | Żółw 'name_1' idzie o 10 kroków naprzód                                                                                           |
| `name_1.turnRight();`<br>`name_1.turnLeft();`                                                                                                                                                                                                                                                                                              | Żółw 'name_1' skręca w prawo/lewo o $90^o$ (względem aktualnej orientacji)                                                        |
| `a = null;`<br>`b = 10;`<br>`c = "c";`<br>`d = "text";`<br>`f = true;`<br>`g = false;`                                                                                                                                                                                                                                                     | Tworzenie zmiennych<br>Domyślna wartość: null<br>Dopuszczalne typy danych: null, integer, real number, character, string, boolean |
| `pos_x = name_1.position.x;`<br>`if(pos_x > 50) {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name_1.turnRight();`<br>`}`<br>`elif(pos_x < -15) {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name_1.turnLeft();`<br>`}`<br>`elif(pos_x >= 10) {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name_1.turnRight();`<br>`}`<br>`else {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`print("else");`<br>`}` | Złożony warunek                                                                                                                   |
| `if(a == 5 and b < 10) {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name_1.forward(2);`<br>`}`                                                                                                                                                                                                                                                           | Prostszy warunek                                                                                                                  |
| `exampleList = [1, 2, 3, 'a', "text"];`<br>`exampleList.append(2);`<br>`exampleList.append("b");`<br>`print(exampleList[2]);`                                                                                                                                                                                                              | Utworzenie listy, dodanie elementu do listy (na koniec), odczytanie elementu spod podanego indeksu                                |
| `for(element in list) {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`print(element);`<br>`}`                                                                                                                                                                                                                                                               | Przykład pętli for                                                                                                                |
| `while(a > b or a > 10) {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`a -= 1;`<br>`}`                                                                                                                                                                                                                                                                     | Przykład pętli while                                                                                                              |
| `foo(param1, param2) {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`i = 10;`<br>&nbsp;&nbsp;&nbsp;&nbsp;`return i + param1 * param2;`<br>`}`<br>`bar() {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`print(foo(50, 20));`<br>`}`<br>                                                                                                                                      | Definicja i wywołanie funkcji 'foo'                                                                                               |
| `fun() {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`print("debug");`<br>`}`                                                                                                                                                                                                                                                                              | Drugi przykład funkcji                                                                                                            |

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

functionDef         = identifier, "(", paramsList, ")", block;
paramsList          = [identifier, {",", identifier}];

block               = "{", {statement}, "}";
statement           = simpleStatement, ";"
                    | compoundStatement;
simpleStatement     = expression, [assignment]
                    | returnStatement;
compoundStatement   = ifStatement
                    | forStatement
                    | whileStatement;

assignment          = assignmentOperator, expression;
assignmentOperator  = "="
                    | "+="
                    | "-="
                    | "*="
                    | "/="
                    | "%=";

returnStatement     = "return", returnValues;
returnValues        = [expression, {",", expression}];

ifStatement         = "if", "(", expression, ")", compoundStmtBody,
                      {elifBlock}, [elseBlock];
elifBlock           = "elif", "(", expression, ")", compoundStmtBody;
elseBlock           = "else", compoundStmtBody;

forStatement        = "for", "(", identifier, "in", expression, ")", compoundStmtBody;
whileStatement      = "while", "(", expression, ")", compoundStmtBody;

compoundStmtBody    = statement
                    | block;

expression          = orExpr, {"or", orExpr};
orExpr              = andExpr, {"and", andExpr};
andExpr             = {"not"}, negateExpr;
negateExpr          = compExpr, [compOperator, compExpr];
compOperator        = "=="
                    | "!="
                    | "<="
                    | "<"
                    | ">="
                    | ">"
                    | "in";
compExpr            = sumExpr, {sumOperator, sumExpr};
sumOperator         = "+"
                    | "-";
sumExpr             = mulExpr, {mulOperator, mulExpr};
mulOperator         = "*"
                    | "/"
                    | "//"
                    | "%";
mulExpr             = {sign}, atom;
sign                = "+"
                    | "-";
atomComplex         = atom, {complex};
atom                = identifier
                    | parenthesis
                    | list
                    | literal;
complex             = dotOperator
                    | funCall
                    | listElement;
dotOperator         = ".", identifier;
funCall             = "(", {arguments}, ")";
arguments           = expression, {",", expression};
listElement         = "[", expression, "]";

parenthesis         = "(", expression, ")";
list                = "[", [expression, {",", expression}], "]";
```

## 4. Opis techniczny

### 4.1. Wymagania funkcjonalne

* Projekt składa się z 4 modułów. Trzy z nich dotyczą języka i są to moduły: analizator leksykalny, analizator
  składniowy i interpretera. Czwarty moduł to interfejs graficzny (GUI).
* Lekser odczytuje dane wejściowe (kod użytkownika) ze strumienia wejściowego (`typing.TextIO`), a parser pobiera
  kolejne tokeny poprzez wywołanie odpowiedniej metody leksera (`get_next_token()`).
* Zadaniem leksera jest wydobywanie z kodu kolejnych tekenów.
* Zadaniem parsera jest pobieranie od leksera tokenów i składanie z nich kodu według gramatyki.
* Pobrane identyfikatory funkcji są przechowywane w słowniku. Dzięki temu jest możliwa kontrolowa niepowtarzalność.
* Program jest uruchamiany przez interpreter Pythona w konsoli jako moduł `python3 -m Tutel`.
* Konsola pozostaje otwarta do wyświetlania wartości podanej do funkcji `print` oraz wczytywania danych od użytkownika
  przez funkcję `input`.
* Obiekty są przekazywane do funkcji jako referencja, a zmienne prostego typu jako wartość.
* Niedopuszczalne jest tworzenie funkcji i zmiennych o takiej samej nazwie jak słowa kluczowe języka.
* Niedopuszczalne jest wielokrotne definiowanie funkcji o takiej samej nazwie.
* Po uruchomieniu programu zostaje wyświetlony interfejs graficzny z podziałem na część do pisania kodu oraz część
  wyświetlającą wykonanie skryptu. Możliwe jest dowolne dostosowanie podziału okna na te dwa elementy.
* Jest możliwość ukrycia jednej z tych części i wyświetlenie drugiej w pełnym oknie.
* Użytkownik może utworzyć nowy skrypt, otworzyć skrypt z pliku na dysku i zapisać swój skrypt do pliku.
* Interfejs przy uruchomieniu wyświetla listę rozwijaną do wyboru funkcji, od której rozpocznie się wykonanie programu.
* Obsługa błędów:
    * Błędy leksera/parsera: program nie zostanie wykonany, rzucony zostanie odpowiedni wyjątek przy pierwszym
      napotkanym błędzie leksykalnym/gramatycznym wraz z położeniem w pliku.
    * Błędy wykonania: program przerwie wykonanie w momencie napotkania błędu i rzuci odpowiedni wyjątek, który może być
      złapany na poziomie GUI.

### 4.2. Wymagania niefunkcjonalne

* Projekt został napisany w języku Python v3.10.
* Do interfejsu graficznego użyta została biblioteka PySide6 (bibliotekę niemal bliźniaczą do PyQt6) w aktualnie
  najnowszej wersji.
* Docelowo aplikacja będzie mogła być uruchomiona na każdym systemie wspierającym Pythona w wybranej wersji i PySide6.
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

W celu przetestowania aplikacji zostało wykonane 368 testów jednostkowych, które zapewniły pokrycie kodu na poziomie
97%.
Dodatkowo do testów manualnych zostały napisane 4 przykładowe skrypty, każdy z nich wykonuje się bez problemów.

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
* Testy jednostkowe sprawdzające rozpoznanie różnych tokenów w bardziej skomplikowanych sekwencjach:
    * jednoliniowych,
    * wieloliniowych.
* Testy jednostkowe sprawdzające kontrolę błędów, czyli wykrywanie błędów leksykalnych i rzucanie odpowiednich wyjątków
  oraz wykrywanie tokenów:
    * T_UNKNOWN - nierozpoznany symbol,
    * T_ILLEGAL - symbol niedozwolony (przerwanie stałej tekstowej znakiem nowej linii lub ETX, przekroczenie
      maksymalnej długości identyfikatora/komentarza/stałej tekstowej, przekroczenie maksymalnego romiaru liczby itp.).

### 5.2. Testowanie parsera

* Testy jednostkowe sprawdzające parsowanie przykładów wszystkich struktur, włączając w to przypadki rzadkie.
* Testy jednostkowe sprawdzające kontrolę błędów, czyli wykrywanie błędów gramatycznych i rzucanie odpowiednich
  wyjątków.
* Dodatkowo dążąc do pełnego pokrycia kodu testami napisałem testy sprawdzające poprawność generowania odpowiednich
  obiektów drzewa kodu.

### 5.4. Testowanie interpretera

* Testy jednostkowe próbujące wykonać wiele różnych fragmentów kodu i sprawdzające czy nie został rzucony żaden wyjątek.
* Testy jednostkowe celowo próbujące wykonać błędny kod i sprawdzające czy odpowiedni wyjątek został rzucony.
* Testy jednostkowe sprawdzające użycie wbudowanych klas/funkcji języka.
* Testy sprawdzające czy wykonanie zacznie się od zadanej funkcji.

## 6. Użytkowanie
### 6.1. Wymagania

* Python 3.10+

### 6.2. Instalacja

```console
$ python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple Tutel --upgrade
```