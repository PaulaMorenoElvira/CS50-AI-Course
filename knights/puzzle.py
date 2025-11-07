from logic import *

AKnight = Symbol("A is a Knight") #Statement that actor A says
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Or(AKnight,AKnave),# Reglas generales: puede ser una u otra
    Not(And(AKnight, AKnave)),# Pero no puede ser las dos

    Implication(AKnight,And(AKnight,AKnave)), # Si A es knight, dice la vdd
    Implication(AKnave,Not(And(AKnight,AKnave))) # SI A es knave, miente

)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And( # Seguimos teniendo las mismas reglas generales, añadiendo ahora al jugador B:
    Or(AKnight,AKnave), # puede ser una u otra
    Not(And(AKnight, AKnave)),# Pero no puede ser las dos

    Or(BKnight,BKnave), # puede ser una u otra
    Not(And(BKnight, BKnave)),# Pero no puede ser las dos

    Implication(AKnight, And(AKnave, BKnave)), # Si A es un knight, no puede mentir
    Implication(AKnave, Not(And(AKnave, BKnave))) #Si A es knave, miente
    
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And( #Seguimos teniendo las mismas reglas generales
    Or(AKnight,AKnave), 
    Not(And(AKnight, AKnave)),

    Or(BKnight,BKnave), 
    Not(And(BKnight, BKnave)),

    Implication(AKnight, Or(And(AKnight,BKnight),And(AKnave, BKnave))), # Si A es un knight, no puede mentir
    Implication(AKnave, Not(Or(And(AKnight,BKnight),And(AKnave, BKnave)))), # Si A es knave, miente

    Implication(BKnight, Or(And(AKnight,BKnave),And(AKnave, BKnight))), # Si B es un knight,  dice la vdd
    Implication(BKnave, Not(Or(And(AKnight,BKnave),And(AKnave, BKnight)))) # Si B es knave, miente
    )

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."

# Hay que crear 2 symbols nuevos, porque aqui no estamos hablando de lo que es, sino del estatement que hace el jugador A
A_said_knight = Symbol("A said Knight")
A_said_knave = Symbol("A said Knave")


knowledge3 = And( #Añadimos jugador C a las reglas generales
    Or(AKnight,AKnave), 
    Not(And(AKnight, AKnave)),

    Or(BKnight,BKnave), 
    Not(And(BKnight, BKnave)),

    Or(CKnight,CKnave), 
    Not(And(CKnight, CKnave)),

    # A dice una de las dos frases, no puede decir las 2 ( sin esto el sistema puede asumir que A no dice nada y no funcionar)
    Or(A_said_knight, A_said_knave),
    Not(And(A_said_knight, A_said_knave)),
    
    Implication(And(AKnight, A_said_knight), AKnight), # Si A es knight, y dijo "soy knight", entonces A es knight
    Implication(And(AKnight, A_said_knave), AKnave), # Si A es knight, y dijo "soy knave", entonces A es knave
    
    Implication(And(AKnave, A_said_knight), Not(AKnight)), # Si A es knave, y dijo "soy knight", entonces A no es knight
    Implication(And(AKnave, A_said_knave), Not(AKnave)), # Si A es knave, y dijo "soy knave", entonces A no es knave
    
    # B es Knight → su afirmación sobre A es verdadera
    Implication(BKnight, A_said_knave),
    # B es Knave → su afirmación sobre A es falsa
    Implication(BKnave, Not(A_said_knave)),

    Implication(BKnight, CKnave),
    Implication(BKnave, Not(CKnave)),


    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight)))


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()


 