#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "SkeletonReferenceHelper.generated.h"

UCLASS()
class ASSETVALIDATOREDITOR_API USkeletonReferenceHelper : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Skeletal Mesh Props")
	static TArray<FString> GetSkeletonBoneNames(USkeletalMesh* Mesh);

	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Skeletal Mesh Props")
	static TArray<int32> GetReferenceSkeletonIndices(USkeletalMesh* Mesh);

};