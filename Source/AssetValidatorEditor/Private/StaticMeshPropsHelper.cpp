#include "StaticMeshPropsHelper.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"

bool UStaticMeshPropsHelper::HasDegenerateTriangles(UStaticMesh* Mesh)
{
    if (!Mesh)
        return false;
    FMeshDescription* MeshDescription = Mesh->GetMeshDescription(0);
    if (!MeshDescription)
        return false;

    FMeshAttributes Attributes(*MeshDescription);
    const TVertexAttributesRef<FVector3f> Positions = Attributes.GetVertexPositions();
    const TTriangleAttributesRef<TArrayView<FVertexID>> VertexIndices =Attributes.GetTriangleVertexIndices();

    constexpr float Epsilon = 0.000001f;

    for (const FTriangleID& TriangleID : MeshDescription->Triangles().GetElementIDs())
    {
        const TArrayView<FVertexID> Verts = VertexIndices[TriangleID];

        const FVector3f A = Positions[Verts[0]];
        const FVector3f B = Positions[Verts[1]];
        const FVector3f C = Positions[Verts[2]];

        const FVector3f AB = B - A;
        const FVector3f AC = C - A;

        const FVector3f Cross = FVector3f::CrossProduct(AB,AC);

        if (Cross.SquaredLength() < Epsilon)
            return true; 
    }

    return false;
}

bool UStaticMeshPropsHelper::HasSourceNormals(UStaticMesh* Mesh)
{
    if (!Mesh)
        return false;

    FMeshDescription* MeshDescription = Mesh->GetMeshDescription(0);
    if (!MeshDescription)
        return false;

    FStaticMeshConstAttributes Attributes(*MeshDescription);

    const TVertexInstanceAttributesConstRef<FVector3f> Normals = Attributes.GetVertexInstanceNormals();

    for (const FVertexInstanceID& VertexInstance : MeshDescription->VertexInstances().GetElementIDs())
    {
        if (!Normals[VertexInstance].IsNearlyZero())
            return true;
    }
    return false;
}
