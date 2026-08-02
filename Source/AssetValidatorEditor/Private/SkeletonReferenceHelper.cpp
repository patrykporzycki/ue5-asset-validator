#include "SkeletonReferenceHelper.h"
#include "Engine/SkeletalMesh.h"

TArray<FString> USkeletonReferenceHelper::GetSkeletonBoneNames(USkeletalMesh* Mesh)
{
    TArray<FString> BoneNames;
    if (!Mesh)
        return BoneNames;
    const FReferenceSkeleton& ReferenceSkeleton = Mesh->GetRefSkeleton();
    const TArray<FMeshBoneInfo>& BoneInfos = ReferenceSkeleton.GetRefBoneInfo();

    BoneNames.Reserve(BoneInfos.Num());
        for (const FMeshBoneInfo& BoneInfo : BoneInfos)
        {
            BoneNames.Add(BoneInfo.Name.ToString());
        }
    return BoneNames;
}

TArray<int32> USkeletonReferenceHelper::GetReferenceSkeletonIndices(USkeletalMesh* Mesh)
{
    TArray<int32> Indices;
    if (!Mesh)
        return Indices;

    const FReferenceSkeleton & ReferenceSkeleton = Mesh->GetRefSkeleton();
    const TArray<FMeshBoneInfo>& BoneInfos = ReferenceSkeleton.GetRefBoneInfo();


    Indices.Reserve(BoneInfos.Num());
    for (const FMeshBoneInfo& BoneInfo : BoneInfos)
    {
        Indices.Add(BoneInfo.ParentIndex);
    }
    return Indices;
}
