#include "MeshPropsHelper.h"
#include "MeshDescription.h"
#include "MeshAttributes.h"
#include "Engine/StaticMesh.h"
#include "Engine/SkeletalMesh.h"

bool UMeshPropsHelper::CheckDegenerateTriangles(FMeshDescription* MeshDescription)
{
    if (!MeshDescription)
        return false;

    FMeshAttributes Attributes(*MeshDescription);
    const TVertexAttributesRef<FVector3f> Positions = Attributes.GetVertexPositions();
    const TTriangleAttributesRef<TArrayView<FVertexID>> VertexIndices = Attributes.GetTriangleVertexIndices();

    constexpr float Threshold = UE_THRESH_POINTS_ARE_SAME;

    for (const FTriangleID& TriangleID : MeshDescription->Triangles().GetElementIDs())
    {
        const TArrayView<FVertexID> Verts = VertexIndices[TriangleID];

        const FVector3f A = Positions[Verts[0]];
        const FVector3f B = Positions[Verts[1]];
        const FVector3f C = Positions[Verts[2]];

        if (A.Equals(B, Threshold) || A.Equals(C, Threshold) || B.Equals(C, Threshold))
            return true;
    }

    return false;
}

bool UMeshPropsHelper::StaticMeshHasDegenerateTriangles(UStaticMesh* Mesh)
{
    if (!Mesh)
        return false;
    for (int32 LODIndex = 0; LODIndex < Mesh->GetNumSourceModels(); ++LODIndex)
    {
        if (CheckDegenerateTriangles(Mesh->GetMeshDescription(LODIndex)))
            return true;
    }
    return false;
}

bool UMeshPropsHelper::SkeletalMeshHasDegenerateTriangles(USkeletalMesh* Mesh)
{
    if (!Mesh)
        return false;
    for (int32 LODIndex = 0; LODIndex < Mesh->GetLODNum(); ++LODIndex)
    {
        if (CheckDegenerateTriangles(Mesh->GetMeshDescription(LODIndex)))
            return true;
    }
    return false;
}

bool UMeshPropsHelper::StaticMeshHasLightmapUVs(UStaticMesh* Mesh)
{
    if (!Mesh)
        return false;

    const int32 LightmapUVIndex = Mesh->GetLightMapCoordinateIndex();
    if (LightmapUVIndex <= 0)
        return false;

    const FMeshDescription* MeshDescription = Mesh->GetMeshDescription(0);
    if (!MeshDescription)
        return false;

    return MeshDescription->GetNumUVElementChannels() > LightmapUVIndex;
}
