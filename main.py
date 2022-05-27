import git
import time
import subprocess

from pathlib import Path


from helpers.util import load_config


def get_repo_name(repo: git.Repo) -> str:
    repo_name = repo.working_tree_dir.split("/")[-1]
    return repo_name


def run_script(path: str) -> bool:
    print(f'Running script: {path}')
    result = subprocess.Popen(path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = result.communicate()
    exit_code = result.returncode

    print(out.decode('utf-8')[:-1])
    print(f'Script exited with code: {exit_code}')

    return exit_code == 0


def get_credentials(cfg: dict) -> dict:
    if cfg["username"] and cfg["password"]:
        return {"username": cfg["username"], "password": cfg["password"]}

    elif cfg["token"]:
        return {"token": cfg["token"]}

    else:
        raise ValueError("Credentials must contain either username and password or github access token")


class Deployable:
    def __init__(self, repo_cfg: dict) -> None:
        """
        A deployable is a github repo that can be deployed automatically by AutoDeployer.
        :param repo_cfg: A dictionary containing a watchable repo config
        :rtype: None
        """
        self.dir = Path(repo_cfg["dir"])
        self.local = git.Repo(self.dir)
        self.remote = git.remote.Remote(self.local, 'origin')
        self.credentials = get_credentials(repo_cfg["credentials"])
        self.install_scripts = [Path(self.dir, script) for script in repo_cfg["install"]]
        self.run_scripts = [Path(self.dir, script) for script in repo_cfg["run"]]

    def check_update(self) -> bool:
        local_timestamp = self.local.head.commit.committed_date
        remote_timestamp = self.remote.fetch()[0].commit.committed_date

        return remote_timestamp > local_timestamp

    def update_local(self) -> None:
        self.remote.pull()

    def install(self) -> bool:
        for script in self.install_scripts:
            path = str(script)
            try:
                run_script(path)

            except Exception:
                return False

        return True

    def run(self) -> bool:
        for script in self.run_scripts:
            path = str(script)
            try:
                run_script(path)

            except Exception:
                return False

        return True


class AutoDeployer:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.deployables = self.get_deployables()
        self.frequency = cfg['frequency']

    def get_deployables(self) -> list[Deployable]:
        deployables = []
        for repo in self.cfg['repos']:
            deployables.append(Deployable(repo))

        return deployables

    def check_deployables(self):
        for deployable in self.deployables:
            name = get_repo_name(deployable.local)
            if deployable.check_update() or True:
                deployable.update_local()
                print(f'{name}: Updated local.')

                print(f'{name}: Installing latest version...')
                success = deployable.install()
                if not success:
                    print(f'{name}: Failed to install.')
                    continue
                print(f'{name}: Installed.')

                print(f'{name}: Running latest version...')
                success = deployable.run()
                if not success:
                    print(f'{name}: Failed to run.')
                    continue
                print(f'{name}: Done.')

            else:
                print(f'{name}: No changes found.')

    def run(self):
        sleep_time = self.frequency
        while True:
            print('Checking for updates...')
            self.check_deployables()
            print(f'Sleeping for {sleep_time} seconds')
            time.sleep(sleep_time)


def main():
    cfg = load_config()
    ad = AutoDeployer(cfg)
    ad.run()


if __name__ == '__main__':
    main()

