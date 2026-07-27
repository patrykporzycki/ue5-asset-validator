#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "PackageLoaderManager.generated.h"

UCLASS()
class ASSETVALIDATOREDITOR_API UPackageLoaderManager : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Loading")
	static TArray<FString> GetLoadedPackageNames();

	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Loading")
	static void UnloadLoadedPackages(const TArray<FString>& KeepLoaded);

	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Loading")
	static int GetLoadedPackageCount();
};