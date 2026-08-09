#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "StaticMeshPropsHelper.generated.h"

UCLASS()
class ASSETVALIDATOREDITOR_API UStaticMeshPropsHelper : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Static Mesh Props")
	static bool HasDegenerateTriangles(UStaticMesh* Mesh);

	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Static Mesh Props")
	static bool HasSourceNormals(UStaticMesh* Mesh);
};