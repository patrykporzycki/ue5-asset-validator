#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MeshPropsHelper.generated.h"

UCLASS()
class ASSETVALIDATOREDITOR_API UMeshPropsHelper : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Mesh Props")
	static bool StaticMeshHasDegenerateTriangles(UStaticMesh* Mesh);

	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Mesh Props")
	static bool SkeletalMeshHasDegenerateTriangles(USkeletalMesh* Mesh);

	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Mesh Props")
	static bool StaticMeshHasLightmapUVs(UStaticMesh* Mesh);

private:
	static bool CheckDegenerateTriangles(FMeshDescription* MeshDescription);
};
