#include "PackageLoaderManager.h"
#include "UObject/Package.h"
#include "UObject/UObjectGlobals.h"
#include "UObject/UObjectHash.h"
#include "UObject/UObjectIterator.h"
#include "Misc/PackageName.h"
#include "Modules/ModuleManager.h"
#include "PackageTools.h"


int UPackageLoaderManager::GetLoadedPackageCount()
{
	int Count = 0;
	for (TObjectIterator<UPackage> It; It; ++It)
	{
		UPackage* Package = *It;
		if (!Package->HasAnyPackageFlags(PKG_InMemoryOnly) && Package->HasAnyFlags(RF_WasLoaded))
		{
			Count++;
		}
	}
	return Count;
}

TArray<FString> UPackageLoaderManager::GetLoadedPackageNames()
{
	TArray<FString> Names;
	for (TObjectIterator<UPackage> It; It; ++It)
	{
		UPackage* Package = *It;
		if (!Package->HasAnyPackageFlags(PKG_InMemoryOnly) && Package->HasAnyFlags(RF_WasLoaded))
		{
			Names.Add(Package->GetName());
		}
	}
	return Names;
}

void UPackageLoaderManager::UnloadLoadedPackages(const TArray<FString>& KeepLoaded)
{
	TSet<FString> Keep(KeepLoaded);

	TArray<UPackage*> ToUnload;
	for (TObjectIterator<UPackage> It; It; ++It)
	{
		UPackage* Package = *It;
		if (!Package->HasAnyPackageFlags(PKG_InMemoryOnly) && Package->HasAnyFlags(RF_WasLoaded))
		{
			if (!Keep.Contains(Package->GetName()))
			{
				ToUnload.Add(Package);
			}
		}
	}

	if (ToUnload.Num() > 0)
	{
		UE_LOG(LogTemp, Display,
			TEXT("UnloadPackagesExcept: unloading %d packages (keeping %d)"),
			ToUnload.Num(), KeepLoaded.Num());

		UPackageTools::UnloadPackages(ToUnload);
	}
}


IMPLEMENT_MODULE(FDefaultModuleImpl, AssetValidatorEditor);
