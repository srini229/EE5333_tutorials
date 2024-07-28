\Problem name: Matching

Minimize
OBJROW: - x_0_1 - x_0_2 - x_1_2 - x_1_3 - x_2_4 - x_3_4 - x_3_5
Subject To
constr(0):  x_0_1 + x_0_2 <= 1
constr(1):  x_0_1 + x_1_2 <= 1
constr(2):  x_0_1 + x_1_3 <= 1
constr(3):  x_0_2 + x_1_2 <= 1
constr(4):  x_0_2 + x_2_4 <= 1
constr(5):  x_1_2 + x_1_3 <= 1
constr(6):  x_1_2 + x_2_4 <= 1
constr(7):  x_1_3 + x_3_4 <= 1
constr(8):  x_1_3 + x_3_5 <= 1
constr(9):  x_2_4 + x_3_4 <= 1
constr(10):  x_3_4 + x_3_5 <= 1
Bounds
 0 <= x_0_1 <= 1
 0 <= x_0_2 <= 1
 0 <= x_1_2 <= 1
 0 <= x_1_3 <= 1
 0 <= x_2_4 <= 1
 0 <= x_3_4 <= 1
 0 <= x_3_5 <= 1
Integers
x_0_1 x_0_2 x_1_2 x_1_3 x_2_4 x_3_4 x_3_5 
End
