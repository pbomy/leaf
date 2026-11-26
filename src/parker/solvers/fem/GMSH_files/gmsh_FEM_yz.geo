SetFactory("OpenCASCADE");




// ----------------------
// DIMENSIONS GLOBALES
// ----------------------

stack_height = N*d + (N-1)*s;

// ----------------------
// DOMAINE GLOBAL
// ----------------------
Disk(1) = {0,0,0,rayon,rayon};

// ----------------------
// LAMES
// ----------------------
For i In {0:N-1}
    y_pos = -stack_height/2 + i*(d+s);
    Rectangle(10+i) = {-b/2, y_pos, 0, b, d};
EndFor

// ----------------------
// DIFFERENCE FLUIDE - LAMES
// ----------------------
plates[] = {};
For i In {0:N-1}
    plates[] += {10+i};
EndFor

BooleanDifference{ Surface{1}; Delete; }{Surface{plates[]};Delete; }

// ----------------------
// GROUPES PHYSIQUES
// ----------------------
Physical Surface("Fluide") = {2};
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
Mesh 2;
Coherence;
//+Recursive Delete {  Curve{26}; }
