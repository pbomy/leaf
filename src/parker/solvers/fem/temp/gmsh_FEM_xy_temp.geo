SetFactory("OpenCASCADE");

d = 0.002; 
b = 0.06; 
L = 0.5; 
N = 5; 
s = 0.06; 
chi = 0; 

taille_maille_min = 0.002; 
taille_maille_max = 0.03; 
rayon = 0.375; 




// ----------------------
// DIMENSIONS GLOBALES
// ----------------------

chi = chi*Pi/180;

stack_height = N*d + (N-1)*s*Cos(chi);   // Hauteur cumulée
stack_breadth = (N-1)*s*Sin(chi)+b;   // Largeur cumulée     

// ----------------------
// DOMAINE GLOBAL
// ----------------------
Disk(1) = {0,0,0,rayon,rayon};

// ----------------------
// LAMES
// ----------------------
For i In {0:N-1}
    y_pos = -stack_height/2 + i*(d+s*Cos(chi));
    x_pos = -stack_breadth/2 + i*s*Sin(chi);
    Rectangle(10+i) = {x_pos, y_pos, 0, b, d};
EndFor

// ----------------------
// DIFFERENCE FLUIDE - LAMES
// ----------------------
plates[] = {};
For i In {0:N-1}
    plates[] += {10+i};
EndFor

fluid[] = BooleanDifference{ Surface{1}; Delete; }{Surface{plates[]};Delete; };

// ----------------------
// GROUPES PHYSIQUES
// ----------------------
// Physical Surface("Fluide") = {fluid[]};
//Physical Surface("Lames") = {plates[]};

// ----------------------
// MAILLAGE
// ----------------------
Mesh.CharacteristicLengthMin = taille_maille_min;
Mesh.CharacteristicLengthMax = taille_maille_max;

Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeExtendFromBoundary = 0;

Field[1] = MathEval;
Field[1].F = Sprintf("%g + (%g-%g)*(x*x+y*y)/(%g*%g)",taille_maille_min, taille_maille_max, taille_maille_min, rayon, rayon);
Background Field = 1;

Mesh 2;//+
Coherence;
